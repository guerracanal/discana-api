import os
import multiprocessing

bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
workers = 1  # Para Cloud Run mejor 1 worker
threads = 4  # Más threads para manejar requests
worker_class = "gthread"
worker_connections = 1000
timeout = 600  # Más tiempo para cold starts
keepalive = 120
max_requests = 1000
max_requests_jitter = 50
preload_app = False  # Correcto para lazy loading