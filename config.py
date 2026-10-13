import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "med-symptom-assistant-secret-key-24cs2506")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
    PORT = int(os.getenv("PORT", 5000))
    HOST = os.getenv("HOST", "127.0.0.1")

    # LLM Settings
    # Options: 'openai', 'ollama', 'auto', 'fallback'
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto").lower()
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Ollama settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

    # Storage settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    
    # Ensure reports directory exists
    os.makedirs(REPORTS_DIR, exist_ok=True)
