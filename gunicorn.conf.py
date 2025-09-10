# gunicorn.conf.py
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
workers = 3  # Adjust as needed
threads = 2  # Adjust as needed
timeout = 1000 # Adjust as needed
graceful_timeout = 300 # Adjust as needed

# ... other Gunicorn settings ...
