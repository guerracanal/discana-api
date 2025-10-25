import os
import multiprocessing

# --- Server Socket ---
# Binds Gunicorn to the specified host and port.
# It listens on all network interfaces (0.0.0.0) and uses the PORT environment variable,
# with a fallback to 8080, which is standard for cloud platforms.
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# --- Worker Processes ---
# The worker_class determines how requests are handled.
# 'gthread' uses a thread pool, which is ideal for I/O-bound applications like APIs
# that spend time waiting for database or external service responses.
worker_class = "gthread"

# For serverless environments like Cloud Run, it's best practice to use only one worker process.
# Scaling is handled by launching more container instances, not by forks within the container.
workers = 1

# The number of threads for handling concurrent requests.
# A single worker process with multiple threads can handle many simultaneous connections efficiently.
threads = 4 

# --- Worker Lifecycle ---
# The maximum number of requests a worker will process before gracefully restarting.
# This is a simple and effective way to combat memory leaks and keep workers healthy.
max_requests = 1000

# Adds a random jitter to max_requests to prevent all workers from restarting at the same time.
# This avoids a "thundering herd" problem and ensures service availability.
max_requests_jitter = 50

# If a worker is silent for more than this number of seconds, it is killed and restarted.
# The 600-second (10-minute) timeout is generous, providing ample time for slow operations
# and protecting against failures during long "cold starts" in serverless environments.
timeout = 600

# --- Keep-Alive ---
# The number of seconds to wait for requests on a keep-alive connection.
# A longer keep-alive helps performance for clients that make multiple requests in a row.
keepalive = 120

# --- Application Loading ---
# If set to True, the application code is loaded once in the master process.
# Setting it to False (recommended) loads the app in each worker process individually.
# This improves robustness, especially for database connections, and supports zero-downtime reloads.
preload_app = False
