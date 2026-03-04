import os
from dotenv import load_dotenv

load_dotenv()

# We use OPENAI_BASE_URL to allow pointing to local models (e.g., Ollama, LM Studio) if desired
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini") # Default to a fast model
