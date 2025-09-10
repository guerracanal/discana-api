# gunicorn.conf.py
bind = "0.0.0.0:8080"  # Or your desired bind address and port
workers = 1  # Adjust as needed
threads = 2  # Adjust as needed
timeout = 300 # Adjust as needed
graceful_timeout = 300 # Adjust as needed

# ... other Gunicorn settings ...
