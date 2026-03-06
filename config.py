import os
from dotenv import load_dotenv

load_dotenv()

# LLM Provider — "groq" | "gemini" | "openai" | "anthropic" | "ollama"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

# Ollama (local)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llama3.2-vision")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Groq (cloud — free tier)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "llama-3.2-11b-vision-preview")

# Gemini (Google — free tier)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_VISION_MODEL = os.getenv("GEMINI_VISION_MODEL", "gemini-2.0-flash")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
ANTHROPIC_VISION_MODEL = os.getenv("ANTHROPIC_VISION_MODEL", "claude-sonnet-4-6")

# Data limits
MAX_DATA_CHARS = int(os.getenv("MAX_DATA_CHARS", "6000"))
MAX_CHAT_HISTORY = int(os.getenv("MAX_CHAT_HISTORY", "10"))

# Supported file types
SUPPORTED_FILE_EXTENSIONS = ["csv", "xlsx", "xls", "json", "pdf", "txt"]
SUPPORTED_IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "webp"]
ALL_SUPPORTED_EXTENSIONS = SUPPORTED_FILE_EXTENSIONS + SUPPORTED_IMAGE_EXTENSIONS

# Multi-lingual
MULTILINGUAL_ENABLED = os.getenv("MULTILINGUAL_ENABLED", "true").lower() == "true"
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")

# RAG (Phase 2)
RAG_ENABLED = os.getenv("RAG_ENABLED", "false").lower() == "true"
RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
RAG_COLLECTION_NAME = os.getenv("RAG_COLLECTION_NAME", "report_agent_docs")

# Memory (Phase 2)
MEMORY_DB_PATH = os.getenv("MEMORY_DB_PATH", "chat_memory.db")

# Provider metadata for UI
PROVIDER_INFO = {
    "groq": {
        "label": "Groq",
        "icon": "⚡",
        "speed": "~500 tok/s",
        "badge": "FASTEST FREE",
        "badge_color": "#10b981",
        "desc": "Llama 3.3 70B · Free tier · 6K req/day",
        "key_env": "GROQ_API_KEY",
        "key_url": "https://console.groq.com",
        "key_placeholder": "gsk_...",
        "needs_key": True,
        "card_bg": "linear-gradient(135deg,#0a1f0a,#051a12)",
        "card_border": "rgba(16,185,129,.25)",
        "card_glow": "rgba(16,185,129,.3)",
    },
    "gemini": {
        "label": "Gemini Flash",
        "icon": "✨",
        "speed": "~400 tok/s",
        "badge": "BEST VISION",
        "badge_color": "#3b82f6",
        "desc": "Google Gemini 2.0 · Free tier · Best for images",
        "key_env": "GEMINI_API_KEY",
        "key_url": "https://aistudio.google.com",
        "key_placeholder": "AIza...",
        "needs_key": True,
        "card_bg": "linear-gradient(135deg,#0a0f2a,#051220)",
        "card_border": "rgba(59,130,246,.25)",
        "card_glow": "rgba(59,130,246,.3)",
    },
    "openai": {
        "label": "OpenAI",
        "icon": "🤖",
        "speed": "~200 tok/s",
        "badge": "GPT-4o",
        "badge_color": "#06b6d4",
        "desc": "GPT-4o-mini (fast & cheap) · GPT-4o for vision",
        "key_env": "OPENAI_API_KEY",
        "key_url": "https://platform.openai.com/api-keys",
        "key_placeholder": "sk-...",
        "needs_key": True,
        "card_bg": "linear-gradient(135deg,#051a1f,#040f18)",
        "card_border": "rgba(6,182,212,.25)",
        "card_glow": "rgba(6,182,212,.3)",
    },
    "anthropic": {
        "label": "Claude",
        "icon": "🧠",
        "speed": "~180 tok/s",
        "badge": "SMARTEST",
        "badge_color": "#f59e0b",
        "desc": "Claude Sonnet 4.6 · Best reasoning & analysis",
        "key_env": "ANTHROPIC_API_KEY",
        "key_url": "https://console.anthropic.com",
        "key_placeholder": "sk-ant-...",
        "needs_key": True,
        "card_bg": "linear-gradient(135deg,#1f1505,#120d03)",
        "card_border": "rgba(245,158,11,.25)",
        "card_glow": "rgba(245,158,11,.3)",
    },
    "ollama": {
        "label": "Ollama",
        "icon": "🖥️",
        "speed": "Varies",
        "badge": "100% LOCAL",
        "badge_color": "#7c3aed",
        "desc": "Llama 3 on your machine · Private · No API key",
        "key_env": None,
        "key_url": None,
        "key_placeholder": None,
        "needs_key": False,
        "card_bg": "linear-gradient(135deg,#1a0a2e,#0f0520)",
        "card_border": "rgba(124,58,237,.25)",
        "card_glow": "rgba(124,58,237,.3)",
    },
}
