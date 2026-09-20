import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DATABASE_PATH = BASE_DIR / "aerotwin.db"

# Load environment variables from .env in project root or backend
env_file_root = ROOT_DIR / ".env"
env_file_backend = BASE_DIR / ".env"
if env_file_root.exists():
    load_dotenv(dotenv_path=env_file_root, override=True)
elif env_file_backend.exists():
    load_dotenv(dotenv_path=env_file_backend, override=True)
else:
    load_dotenv(override=True)

class Settings(BaseModel):
    app_name: str = "AeroTwin AI - MALE UAV Aero-Piston Engine Digital Twin"
    version: str = "1.0.0"
    db_path: str = str(DATABASE_PATH)
    simulation_tick_hz: float = 2.0  # Telemetry updates 2 times per second
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

settings = Settings()
