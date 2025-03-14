from app import app  # Asegúrate de que "app" sea la instancia de Flask

if __name__ == "__main__":
    app.run()  # Esto solo se ejecuta localmente, Gunicorn ignora este bloque