from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=BASE_DIR / ".env")
# load_dotenv()  # take environment variables from .env file

@dataclass(frozen=True)
class Settings:
    # Token endpoint for both code exchange & refresh flow
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"
    
    CLIENT_ID = os.getenv("YT_CLIENT_ID")
    CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")

    YOUTUBE_CHANNEL_ID: str | None = os.getenv("YOUTUBE_CHANNEL_ID")

    # Store secrets separately
    # why are we storing refresh token separately , is tere any specific reason and more professional way to do it?
    # BASE_DIR = Path(__file__).resolve().parents[1]
    REFRESH_TOKEN_PATH: Path = BASE_DIR / os.getenv("REFRESH_TOKEN_PATH")
    TOKENS_CACHE_PATH: Path = BASE_DIR / os.getenv("TOKENS_CACHE_PATH")

    # Check interval
    CHECK_INTERVAL_SECONDS: int = 30 * 60  # 30 minutes

    # Refresh early so you never hit expiry mid-request
    REFRESH_EARLY_SECONDS: int = 5 * 60   # refresh if <5 min remaining
