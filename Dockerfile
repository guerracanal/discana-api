# Dockerfile para Cloud Run optimizado

FROM python:3.11-slim-bullseye

# Evitar prompts de apt y actualizar paquetes
ENV DEBIAN_FRONTEND=noninteractive

# Instalar librerías del sistema necesarias para OpenCV y otras dependencias nativas
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libgl1-mesa-glx libgl1 libgl1-mesa-dev ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivo de requerimientos e instalar librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto que Cloud Run usará
#ENV PORT=8080
#EXPOSE 8080

# Comando para arrancar Gunicorn
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
