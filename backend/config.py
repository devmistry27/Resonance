"""
Backend Configuration Module
Loads settings from environment variables with sensible defaults.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# Logging Configuration
# =============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# =============================================================================
# Base Paths
# =============================================================================
BASE_DIR = Path(__file__).parent.resolve()
MODEL_DIR = BASE_DIR / "model"

# =============================================================================
# Model Configuration
# =============================================================================
MODEL_PATH = os.getenv("MODEL_PATH", str(MODEL_DIR / "gpt2-large774M-sft.pth"))
DEVICE = os.getenv("DEVICE", "cuda")  # "cuda" or "cpu"

# Model Architecture (GPT-2 Large by default)
MODEL_EMB_DIM = int(os.getenv("MODEL_EMB_DIM", "1280"))
MODEL_N_LAYERS = int(os.getenv("MODEL_N_LAYERS", "36"))
MODEL_N_HEADS = int(os.getenv("MODEL_N_HEADS", "20"))

# =============================================================================
# Generation Settings
# =============================================================================
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "1024"))
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "256"))

# Temperature settings - lower for factual queries
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
FACTUAL_TEMPERATURE = float(os.getenv("FACTUAL_TEMPERATURE", "0.3"))  # For search queries

DEFAULT_TOP_P = float(os.getenv("DEFAULT_TOP_P", "0.9"))

# Anti-hallucination settings
REPETITION_PENALTY = float(os.getenv("REPETITION_PENALTY", "1.15"))
MIN_RESPONSE_LENGTH = int(os.getenv("MIN_RESPONSE_LENGTH", "10"))

# =============================================================================
# Search Configuration
# =============================================================================
SEARCH_ENABLED = os.getenv("SEARCH_ENABLED", "true").lower() == "true"
SEARCH_MAX_RESULTS = int(os.getenv("SEARCH_MAX_RESULTS", "3"))
SEARCH_TIMEOUT = int(os.getenv("SEARCH_TIMEOUT", "10"))  # seconds
SEARCH_RETRY_ATTEMPTS = int(os.getenv("SEARCH_RETRY_ATTEMPTS", "2"))

# Keywords that trigger automatic search
SEARCH_TRIGGER_KEYWORDS = [
    "search", "browse", "google", "internet", "lookup", "find online",
    "stock", "price", "today", "current", "latest", "now", "weather",
    "news", "score", "rate", "live", "recent", "update", "2024", "2025",
    "who is", "what is the current", "how much"
]

# =============================================================================
# Server Configuration
# =============================================================================
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", 
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
).split(",")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# =============================================================================
# GPT-2 Model Settings
# =============================================================================
GPT2_MODEL_NAME = "gpt2"
GPT2_VOCAB_SIZE = 50257
GPT2_BLOCK_SIZE = int(os.getenv("GPT2_BLOCK_SIZE", "1024"))
GPT2_EOS_TOKEN_ID = 50256  # 
