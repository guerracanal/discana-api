# gunicorn.conf.py
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
workers = 1         # Inicio rápido, luego Cloud Run escala si es necesario
threads = 1
timeout = 0         # No matar workers mientras arranca la app
graceful_timeout = 30
preload_app = False  # Muy importante: no pre-cargar librerías pesadas