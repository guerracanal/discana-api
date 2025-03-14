import os
from app import app

# Convertir la variable PORT a entero, en caso de que esté como cadena
port = int(os.getenv('PORT', 8080))
if __name__ == "__main__":
    # Usa el valor de la variable 'port' en lugar de un valor fijo
    app.run(host="0.0.0.0", port=port, debug=False)
