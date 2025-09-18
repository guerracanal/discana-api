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
