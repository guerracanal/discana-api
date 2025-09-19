import logging
from flask import Blueprint, jsonify, request
from admin.services import dump_google_sheet_data_to_db

# Configure Blueprint and logging
admin_blueprint = Blueprint("admin", __name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@admin_blueprint.route("/dump-google-sheet-data-to-db", methods=["POST"])
def dump_google_sheet_data_to_db_route():
    """
    API endpoint to trigger dumping data from Google Sheets to a MongoDB collection.
    Expects a JSON payload with 'spreadsheet', 'sheets' (list), 'collection',
    and an optional 'overwrite' (boolean).
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
    sheets = data.get('sheets')
    collection = data.get('collection')
    overwrite = data.get('overwrite', False) # Default to False if not provided

    # Check for mandatory parameters
    if not all([spreadsheet, sheets, collection]):
        logging.warning(f"Missing one or more required parameters. Received: {data}")
        return jsonify({
            "status": "error", 
            "message": "Missing required parameters. Please provide 'spreadsheet', 'sheets' (as a list), and 'collection'."
        }), 400

    # Validate that 'sheets' is a non-empty list
    if not isinstance(sheets, list) or not sheets:
        logging.warning(f"'sheets' parameter must be a non-empty list. Received: {sheets}")
        return jsonify({
            "status": "error",
            "message": "Invalid parameter: 'sheets' must be a non-empty list of sheet names."
        }), 400

    logging.info(f"Request validated. Parameters: spreadsheet='{spreadsheet}', sheets={sheets}, collection='{collection}', overwrite={overwrite}.")

    # 2. Execute the service logic
    try:
        records_inserted = dump_google_sheet_data_to_db(spreadsheet, sheets, collection, overwrite)
        
        if records_inserted > 0:
            message = f"Successfully inserted {records_inserted} records into collection '{collection}'."
            logging.info(message)
            return jsonify({"status": "success", "message": message, "records_inserted": records_inserted})
        else:
            message = f"No new records were inserted. The specified sheets may be empty or contain no data."
            logging.info(message)
            return jsonify({"status": "success", "message": message, "records_inserted": 0})

    except Exception as e:
        logging.error(f"An error occurred during the dump process: {e}", exc_info=True)
        return jsonify({
            "status": "error", 
            "message": f"An internal error occurred. Please check the server logs for details. Error: {e}"
        }), 500

# Debugging routes (remain unchanged)
@admin_blueprint.route("/debug/env", methods=["GET"])
def debug_env_vars():
    import os
    expected_vars = ["GOOGLE_CREDENTIALS_JSON", "MONGO_URI", "GEMINI_API_KEY", "ADMIN_TOKENS"]
    env_status = {}
    for var in expected_vars:
        value = os.environ.get(var)
        if value:
            masked = f"{value[:10]}...{value[-10:]}" if len(value) > 20 else f"{value[:5]}...{value[-2:]}"
            env_status[var] = f"SET ({len(value)} chars): {masked}"
        else:
            env_status[var] = "NOT SET"
    return jsonify({"status": "debug", "environment_variables": env_status, "total_env_vars": len(os.environ)})

@admin_blueprint.route("/debug/google-creds", methods=["GET"])
def debug_google_creds():
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
        all_vars = {k: "SET" for k in os.environ.keys() if "GOOGLE" in k.upper()}
        return jsonify({"status": "NOT_FOUND", "google_vars": all_vars, "total_env_vars": len(os.environ)})
