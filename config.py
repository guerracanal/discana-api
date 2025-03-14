# config.py
import os

# Cargar .env solo si existe (para desarrollo local)
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    # ... otras variables