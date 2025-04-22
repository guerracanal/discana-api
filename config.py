# config.py
import os

class Config:
    API_VERSION = os.environ.get("API_VERSION")
    MONGO_URI = os.environ.get("MONGO_URI")
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
    SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
    SPOTIFY_SECRET = os.environ.get("SPOTIFY_SECRET")
    LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY")
    LASTFM_API_SECRET = os.environ.get("LASTFM_API_SECRET")
    DISCOGS_API_KEY = os.environ.get("DISCOGS_API_KEY")
    DISCOGS_API_SECRET = os.environ.get("DISCOGS_API_SECRET")
    FRONTEND_URL = os.environ.get("FRONTEND_URL")
    API_URL = os.environ.get("API_URL")
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "default_secret_key")  # Cambia "default_secret_key" por algo más seguro

    def check_required_vars(self):
        required_vars = [
            "MONGO_URI", "ENCRYPTION_KEY", "SPOTIFY_CLIENT_ID",
            "SPOTIFY_SECRET", "LASTFM_API_KEY", "LASTFM_API_SECRET",
            "FRONTEND_URL", "API_URL"
        ]
        missing_vars = [var for var in required_vars if not os.environ.get(var)]  # Verifica directamente en os.environ
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

config = Config()
config.check_required_vars()