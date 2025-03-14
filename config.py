import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")  # Esta variable se tomará del archivo .env o del entorno del sistema
    DEBUG = True
