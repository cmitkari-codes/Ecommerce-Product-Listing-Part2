import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-this-secret-key")
    DATABASE = os.environ.get("DATABASE_PATH", str(BASE_DIR / "instance" / "shop.sqlite3"))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "0") == "1"
