FROM python:3.11-slim-bullseye

# Set environment variables for a non-interactive setup and optimized Python execution
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Minimal system dependencies
# We only need pkg-config for some Python packages that might compile C extensions.
# Use retries and Acquire::Retries to make apt-get robust against transient network/timeouts.
RUN set -eux; \
    # try up to 3 times to update/install to mitigate transient network issues
    for i in 1 2 3; do \
        apt-get update && \
        apt-get -o Acquire::Retries=3 install -y --no-install-recommends pkg-config ca-certificates && \
        break || echo "apt-get attempt $i failed, retrying..." && sleep 5; \
    done; \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker layer caching.
# This ensures that dependencies are not re-installed unless the requirements file changes.
COPY requirements.txt .

# Install Python dependencies
# Using --no-cache-dir reduces the image size.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create and switch to a non-root user for better security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Command to run the application using Gunicorn
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
