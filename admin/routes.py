import logging
from flask import Blueprint, jsonify, request
from admin.services import dump_google_sheet_data_to_db

# Configure Blueprint and logging
admin_blueprint = Blueprint("admin", __name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@admin_blueprint.route("/dump-google-sheet-data-to-db", methods=["POST"])
def dump_google_sheet_data_to_db_route():
    """
    API endpoint to trigger the process of dumping data from a Google Sheet to a MongoDB collection.
    Expects a JSON payload with 'spreadsheet', 'sheet', and 'collection'.
    """
    logging.info(f"Received request for /dump-google-sheet-data-to-db from {request.remote_addr}.")
    
    # 1. Validate incoming request
    if not request.is_json:
        logging.warning("Request is not in JSON format.")
        return jsonify({
            "status": "error", 
            "message": "Invalid request: Content-Type must be application/json."
        }), 400

    data = request.get_json()
    spreadsheet = data.get('spreadsheet')
    sheet = data.get('sheet')
    collection = data.get('collection')

    # Check for mandatory parameters
    if not all([spreadsheet, sheet, collection]):
        logging.warning(f"Missing one or more required parameters. Received: {data}")
        return jsonify({
            "status": "error", 
            "message": "Missing required parameters. Please provide 'spreadsheet', 'sheet', and 'collection'."
        }), 400

    logging.info(f"Request validated. Parameters: spreadsheet='{spreadsheet}', sheet='{sheet}', collection='{collection}'.")

    # 2. Execute the service logic
    try:
        records_inserted = dump_google_sheet_data_to_db(spreadsheet, sheet, collection)
        
        if records_inserted > 0:
            message = f"Successfully inserted {records_inserted} records into collection '{collection}' from sheet '{sheet}'."
            logging.info(message)
            return jsonify({"status": "success", "message": message, "records_inserted": records_inserted})
        else:
            message = f"No new records were inserted. The sheet '{sheet}' may be empty or contain no new data."
            logging.info(message)
            return jsonify({"status": "success", "message": message, "records_inserted": 0})

    except Exception as e:
        # The service layer is responsible for logging the specifics of the exception.
        logging.error(f"An error occurred during the dump process: {e}")
        # Return a generic but helpful error message to the client.
        return jsonify({
            "status": "error", 
            "message": f"An internal error occurred. Please check the server logs for details. Error: {e}"
        }), 500


# Añadir a admin/routes.py

@admin_blueprint.route("/debug/env", methods=["GET"])
def debug_env_vars():
    """
    Endpoint de debug para verificar qué variables de entorno están disponibles
    ⚠️ ELIMINAR EN PRODUCCIÓN por seguridad
    """
    import os
    
    # Variables que esperamos
    expected_vars = [
        "GOOGLE_CREDENTIALS_JSON",
        "MONGO_URI", 
        "GEMINI_API_KEY",
        "ADMIN_TOKENS"
    ]
    
    env_status = {}
    for var in expected_vars:
        value = os.environ.get(var)
        if value:
            # Mostrar solo los primeros y últimos caracteres para seguridad
            if len(value) > 20:
                masked = f"{value[:10]}...{value[-10:]}"
            else:
                masked = f"{value[:5]}...{value[-2:]}"
            env_status[var] = f"SET ({len(value)} chars): {masked}"
        else:
            env_status[var] = "NOT SET"
    
    return jsonify({
        "status": "debug",
        "environment_variables": env_status,
        "total_env_vars": len(os.environ)
    })

# En admin/routes.py
@admin_blueprint.route("/debug/google-creds", methods=["GET"])
def debug_google_creds():
    """Debug para verificar GOOGLE_CREDENTIALS_JSON"""
    import os
    
    google_creds = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    
    if google_creds:
        return jsonify({
            "status": "FOUND",
            "length": len(google_creds),
            "starts_with": google_creds[:50] if len(google_creds) > 50 else google_creds,
            "is_valid_json": "yes" if google_creds.startswith('{') else "no"
        })
    else:
        # Listar todas las variables de entorno que empiecen con GOOGLE
        all_vars = {k: "SET" for k in os.environ.keys() if "GOOGLE" in k.upper()}
        return jsonify({
            "status": "NOT_FOUND",
            "google_vars": all_vars,
            "total_env_vars": len(os.environ)
        })