import os
from dotenv import load_dotenv

load_dotenv()

# Your fine-tuned model on Hugging Face Hub.
# Double-check this against your actual model page -- HF sometimes shows a
# different canonical name than the one you typed in push_to_hub().
MODEL_REPO = os.getenv("MODEL_REPO", "lohithg8408/content-moderation")

# SQLite for local dev by default. In production (Render), set DATABASE_URL
# as an environment variable pointing at your Supabase Postgres connection
# string -- no code change needed, SQLAlchemy handles both.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "1000"))
