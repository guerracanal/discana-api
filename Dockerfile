FROM python:3.11-slim-bullseye

# Set environment variables for a non-interactive setup and optimized Python execution
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Minimal system dependencies
# We only need pkg-config for some Python packages that might compile C extensions.
# The rest of the previously listed libraries were related to GUI/media processing and are not needed.
RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

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
