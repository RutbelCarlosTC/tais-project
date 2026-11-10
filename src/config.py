"""
Configuración centralizada del sistema experimental Multiagente vs RAG Convencional.
"""
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Carga de variables de entorno desde .env si existe
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
OUTPUT_DIR = BASE_DIR / f"outputs_nemotron_{time.strftime('%Y%m%d_%H%M%S')}"

# Crear directorios clave si no existen
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

# Parámetros de Ingesta y Vector Store (Arquitectura de Datos y Dominio)
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "600"))        # Entre 500 y 800 tokens aprox.
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "90"))   # 10% - 15% de solapamiento
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "4"))
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence-transformers")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

# Parámetros de LLM
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "nvidia").lower()  # "mock", "openai", "gemini", "ollama", "nvidia"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")

# Parámetros de LLM NVIDIA NIM
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "minimaxai/minimax-m3.1-flash")

# Parámetros de Orquestación Multiagente
MAX_CRITIC_ITERATIONS = int(os.getenv("MAX_CRITIC_ITERATIONS", "3"))
INVEST_PASS_THRESHOLD = float(os.getenv("INVEST_PASS_THRESHOLD", "7.5"))  # Escala 0-10
