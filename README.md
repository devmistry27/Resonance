<p align="center">
  <img src="https://img.shields.io/badge/GPT--2-774M%20Parameters-blue?style=for-the-badge" alt="GPT-2 774M"/>
  <img src="https://img.shields.io/badge/PyTorch-2.1+-red?style=for-the-badge&logo=pytorch" alt="PyTorch"/>
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react" alt="React"/>
  <img src="https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi" alt="FastAPI"/>
</p>

# 🎵 Resonance

A **ChatGPT-style conversational AI** built from scratch with a custom GPT-2 implementation. Features real-time streaming responses, web search integration (RAG), and a modern React interface.

![Resonance Demo](demo.mp4)

---

## ✨ Features

### 🧠 Custom Transformer Architecture
- **Full GPT-2 implementation from scratch** — Multi-Head Attention, LayerNorm, Feed-Forward networks, causal masking
- **Fine-tuned GPT-2 Large (774M parameters)** on instruction-following datasets via Supervised Fine-Tuning (SFT)
- Custom training loop, tokenizer integration, and optimized data pipeline

### ⚡ Real-Time Streaming Inference
- **Token-by-token generation** via Server-Sent Events (SSE)
- OpenAI-compatible API endpoints
- Automatic context window management for extended conversations

### 🔍 RAG Integration
- **Web search retrieval** for context-aware, up-to-date responses
- DuckDuckGo integration with retry logic and result processing
- Automatic query optimization and source attribution

### 💬 Modern Chat Interface
- Beautiful, responsive React 19 UI with TailwindCSS
- Smooth animations with Framer Motion
- Dark mode support with glassmorphism design
- Conversation history management

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Chat Input  │  │  Messages   │  │   Streaming Display     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ SSE / REST
┌────────────────────────────▼────────────────────────────────────┐
│                      FastAPI Backend                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Chat API    │  │  Session    │  │   Search Service        │  │
│  │ (Streaming) │  │  Manager    │  │   (DuckDuckGo RAG)      │  │
│  └──────┬──────┘  └─────────────┘  └─────────────────────────┘  │
│         │                                                        │
│  ┌──────▼──────────────────────────────────────────────────┐    │
│  │                    Model Service                         │    │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │    │
│  │  │ Tokenizer  │  │ Inference  │  │ Context Management │  │    │
│  │  │ (tiktoken) │  │   Engine   │  │                    │  │    │
│  │  └────────────┘  └────────────┘  └────────────────────┘  │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                  Custom GPT-2 Implementation                     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    LLMModel (774M)                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│  │
│  │  │  Token &    │  │ Transformer │  │   Output Head       ││  │
│  │  │  Position   │  │   Blocks    │  │                     ││  │
│  │  │  Embeddings │  │   (×36)     │  │                     ││  │
│  │  └─────────────┘  └──────┬──────┘  └─────────────────────┘│  │
│  │                          │                                 │  │
│  │  ┌───────────────────────▼─────────────────────────────┐  │  │
│  │  │              TransformerBlock                        │  │  │
│  │  │  ┌─────────────────┐  ┌─────────────────┐           │  │  │
│  │  │  │ MultiHeadAttn   │  │  FeedForward    │           │  │  │
│  │  │  │ (20 heads)      │  │  (GELU)         │           │  │  │
│  │  │  └─────────────────┘  └─────────────────┘           │  │  │
│  │  │  + LayerNorm + Residual Connections                  │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** with CUDA support (recommended)
- **Node.js 18+** or **Bun**
- **8GB+ GPU VRAM** for GPT-2 Large (or use CPU with reduced performance)

### 1. Clone the Repository

```bash
git clone https://github.com/devmistry27/resonance.git
cd resonance
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env to set MODEL_PATH and DEVICE settings
```

### 3. Frontend Setup

```bash
cd resonance

# Install dependencies (using bun or npm)
bun install
# or
npm install
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
# Server runs at http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd resonance
bun dev
# or
npm run dev
# App runs at http://localhost:5173
```

---

## 📡 API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check and service status |
| `/v1/chat/completions` | POST | Generate chat completion |
| `/v1/chat/stream` | POST | Streaming chat via SSE |
| `/v1/conversations/{id}` | GET | Get conversation history |
| `/v1/conversations/{id}` | DELETE | Clear conversation |
| `/v1/conversations` | GET | List all sessions |

### Chat Completion Request

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "messages": [
      {"role": "user", "content": "What is machine learning?"}
    ]
  }'
```

### Streaming Request

```bash
curl -X POST http://localhost:8000/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "messages": [
      {"role": "user", "content": "Explain transformers"}
    ],
    "stream": true
  }'
```

### Interactive API Docs

Visit `http://localhost:8000/docs` for Swagger UI documentation.

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance async API framework |
| **PyTorch** | Deep learning & model inference |
| **tiktoken** | OpenAI's fast tokenizer |
| **Transformers** | Model loading utilities |
| **SSE-Starlette** | Server-Sent Events for streaming |
| **DuckDuckGo Search** | Web search for RAG |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 19** | UI framework |
| **TypeScript** | Type safety |
| **Vite** | Build tool |
| **TailwindCSS 4** | Styling |
| **Framer Motion** | Animations |
| **shadcn/ui** | UI components |

---

## 📁 Project Structure

```
resonance/
├── backend/                 # FastAPI backend
│   ├── main.py             # API server & endpoints
│   ├── gpt_model.py        # Custom GPT-2 implementation
│   ├── model_service.py    # Model loading & inference
│   ├── chat_manager.py     # Conversation history management
│   ├── search_service.py   # RAG web search integration
│   ├── config.py           # Configuration settings
│   ├── schemas.py          # Pydantic models
│   └── model/              # Pre-trained model weights
│       ├── gpt2-large774M-sft.pth
│       └── gpt2-medium355M-sft.pth
│
└── resonance/              # React frontend
    ├── src/
    │   ├── components/
    │   │   ├── chat/       # Chat UI components
    │   │   ├── layout/     # Layout components
    │   │   └── ui/         # shadcn/ui components
    │   ├── hooks/          # React hooks
    │   ├── lib/            # Utilities
    │   └── App.tsx         # Main application
    └── package.json
```

---

## 🔧 Configuration

### Environment Variables (`.env`)

```env
# Model Settings
MODEL_PATH=./model/gpt2-large774M-sft.pth
DEVICE=cuda  # or 'cpu'
MAX_NEW_TOKENS=256
CONTEXT_LENGTH=1024

# Server Settings
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=["http://localhost:5173"]

# Search Settings
SEARCH_ENABLED=true
SEARCH_MAX_RESULTS=5
```

---

## 🧪 Model Details

### GPT-2 Large Configuration

| Parameter | Value |
|-----------|-------|
| Parameters | 774M |
| Layers | 36 |
| Hidden Size | 1280 |
| Attention Heads | 20 |
| Context Length | 1024 |
| Vocabulary Size | 50,257 |

### Training

- **Base Model:** GPT-2 Large (OpenAI)
- **Fine-tuning:** Supervised Fine-Tuning (SFT) on instruction-following datasets
- **Objective:** Next-token prediction with instruction formatting

---

## 👥 Team

| Role | Contributor |
|------|-------------|
| **Architecture, Model Training, Inference Engine** | Dev Mistry |
| **React Frontend, UI/UX, Backend Integration** | Hiren Dhola |

---

## 📄 License

This project is for educational and research purposes. The GPT-2 model weights are subject to OpenAI's license terms.

---

## 🔗 Resources

- [Build a Large Language Model (From Scratch)](https://www.manning.com/books/build-a-large-language-model-from-scratch) — Reference architecture

---

<p align="center">
  Built with ❤️ and lots of GPU hours
</p>
