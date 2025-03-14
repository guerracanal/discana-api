# Usar una imagen base oficial de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el código fuente de la app al contenedor
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8080 en el que corre la app
EXPOSE 8080

# Comando para ejecutar la app Flask
CMD ["python", "wsgi.py"]


#gcloud builds submit --tag gcr.io/discana/flask-api
#gcloud run deploy --image gcr.io/discana/flask-app --platform managed
