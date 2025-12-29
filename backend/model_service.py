"""
GPT-2 Model Service
Handles model loading and text generation with anti-hallucination measures.
"""
import torch
import tiktoken
import logging
import os
from typing import Generator, Optional

import config
from gpt_model import LLMModel

logger = logging.getLogger(__name__)


class ModelService:
    """Service for GPT-2 model inference with streaming support."""
    
    def __init__(self):
        self.model: Optional[LLMModel] = None
        self.tokenizer = None
        self.device: Optional[torch.device] = None
        self.is_loaded = False
        
    def load_model(self) -> bool:
        """Load the GPT-2 model and tokenizer."""
        try:
            logger.info(f"Loading model from {config.MODEL_PATH}...")
            
            if config.DEVICE == "cuda" and torch.cuda.is_available():
                self.device = torch.device("cuda")
                logger.info(f"Using CUDA: {torch.cuda.get_device_name(0)}")
            else:
                self.device = torch.device("cpu")
                logger.info("Using CPU")
            
            self.tokenizer = tiktoken.get_encoding("gpt2")
            logger.info("Loaded tiktoken GPT-2 tokenizer")
            
            if not os.path.exists(config.MODEL_PATH):
                raise FileNotFoundError(f"Model not found at {config.MODEL_PATH}")
            
            checkpoint = torch.load(config.MODEL_PATH, map_location=self.device, weights_only=False)
            
            gpt_config = {
                "vocab_size": config.GPT2_VOCAB_SIZE,
                "context_length": config.GPT2_BLOCK_SIZE,
                "drop_rate": 0.0,
                "qkv_bias": True,
                "emb_dim": config.MODEL_EMB_DIM,
                "n_layers": config.MODEL_N_LAYERS,
                "n_heads": config.MODEL_N_HEADS
            }
            
            self.model = LLMModel(gpt_config)
            self.model.load_state_dict(checkpoint)
            self.model.to(self.device)
            self.model.eval()
            
            self.is_loaded = True
            logger.info("Model loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            import traceback
            traceback.print_exc()
            self.is_loaded = False
            return False
    
    def encode(self, text: str) -> list:
        """Encode text to token IDs."""
        eos_token = "<" + "|endoftext|" + ">"
        return self.tokenizer.encode(text, allowed_special={eos_token})
    
    def decode(self, tokens: list) -> str:
        """Decode token IDs to text."""
        return self.tokenizer.decode(tokens)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encode(text))
    
    def _apply_repetition_penalty(self, logits: torch.Tensor, generated_ids: list) -> torch.Tensor:
        """Apply repetition penalty to discourage repeated tokens."""
        if not generated_ids or config.REPETITION_PENALTY == 1.0:
            return logits
            
        for token_id in set(generated_ids[-50:]):  # Check last 50 tokens
            if logits[0, token_id] > 0:
                logits[0, token_id] /= config.REPETITION_PENALTY
            else:
                logits[0, token_id] *= config.REPETITION_PENALTY
        return logits
    
    def _clean_response(self, text: str) -> str:
        """Clean up generated response to remove artifacts."""
        # Remove prompt format leakage
        stop_markers = ["### Instruction:", "### Response:", "User:", "Assistant:"]
        for marker in stop_markers:
            if marker in text:
                text = text.split(marker)[0]
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        return text.strip()

    @torch.no_grad()
    def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None,
        top_p: float = None,
    ) -> tuple:
        """
        Generate text completion.
        Returns: (generated_text, prompt_tokens, completion_tokens)
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        max_tokens = max_tokens or config.DEFAULT_MAX_TOKENS
        temperature = temperature if temperature is not None else config.DEFAULT_TEMPERATURE
        top_p = top_p if top_p is not None else config.DEFAULT_TOP_P
        
        input_ids = self.encode(prompt)
        prompt_tokens = len(input_ids)
        
        max_context = config.GPT2_BLOCK_SIZE
        if len(input_ids) > max_context - max_tokens:
            input_ids = input_ids[-(max_context - max_tokens):]

        idx = torch.tensor([input_ids], dtype=torch.long, device=self.device)
        generated_ids = []
        
        for _ in range(max_tokens):
            idx_cond = idx[:, -config.GPT2_BLOCK_SIZE:]
            logits = self.model(idx_cond)
            logits = logits[:, -1, :]
            
            logits = torch.nan_to_num(logits, nan=0.0, posinf=100.0, neginf=-100.0)
            logits = self._apply_repetition_penalty(logits, generated_ids)

            if temperature > 0:
                logits = logits / temperature
                
                if top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                    cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = 0
                    indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                    logits[indices_to_remove] = float("-inf")
                
                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
            else:
                probs = torch.softmax(logits, dim=-1)
                next_token = torch.argmax(probs, dim=-1, keepdim=True)
            
            token_id = next_token.item()
            
            if token_id == config.GPT2_EOS_TOKEN_ID:
                break
                
            generated_ids.append(token_id)
            idx = torch.cat((idx, next_token), dim=1)

        generated_text = self.decode(generated_ids)
        generated_text = self._clean_response(generated_text)
        
        return generated_text, prompt_tokens, len(generated_ids)

    @torch.no_grad()
    def generate_stream(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None,
        top_p: float = None,
    ) -> Generator:
        """
        Stream text generation token by token.
        Yields: (token_text, is_done, prompt_tokens, completion_tokens)
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        max_tokens = max_tokens or config.DEFAULT_MAX_TOKENS
        temperature = temperature if temperature is not None else config.DEFAULT_TEMPERATURE
        top_p = top_p if top_p is not None else config.DEFAULT_TOP_P
        
        input_ids = self.encode(prompt)
        prompt_tokens = len(input_ids)

        max_context = config.GPT2_BLOCK_SIZE
        if len(input_ids) > max_context - max_tokens:
            input_ids = input_ids[-(max_context - max_tokens):]

        idx = torch.tensor([input_ids], dtype=torch.long, device=self.device)
        generated_ids = []
        
        for _ in range(max_tokens):
            idx_cond = idx[:, -config.GPT2_BLOCK_SIZE:]
            logits = self.model(idx_cond)
            logits = logits[:, -1, :]
            
            logits = torch.nan_to_num(logits, nan=0.0, posinf=100.0, neginf=-100.0)
            logits = self._apply_repetition_penalty(logits, generated_ids)

            if temperature > 0:
                logits = logits / temperature
                if top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                    cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = 0
                    indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                    logits[indices_to_remove] = float("-inf")
                
                probs = torch.softmax(logits, dim=-1)
                idx_next = torch.multinomial(probs, num_samples=1)
            else:
                probs = torch.softmax(logits, dim=-1)
                idx_next = torch.argmax(probs, dim=-1, keepdim=True)
                
            token_id = idx_next.item()
            
            if token_id == config.GPT2_EOS_TOKEN_ID:
                yield "", True, prompt_tokens, len(generated_ids)
                break
                
            generated_ids.append(token_id)
            token_text = self.decode([token_id])
            yield token_text, False, prompt_tokens, len(generated_ids)
            
            idx = torch.cat((idx, idx_next), dim=1)
        else:
            yield "", True, prompt_tokens, len(generated_ids)


# Global model instance
model_service = ModelService()
