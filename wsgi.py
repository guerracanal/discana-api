import os
from app import app

port = os.getenv('PORT', 8080)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
