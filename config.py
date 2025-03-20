# config.py
import os
class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_SECRET = os.getenv("SPOTIFY_SECRET")
    SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
    FRONTEND_REDIRECT_URI = os.getenv("FRONTEND_REDIRECT_URI")