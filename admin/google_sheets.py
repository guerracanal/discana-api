import gspread
import logging
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from collections import Counter

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def to_list(value):
    """Converts a comma-separated string to a list of clean strings."""
    if isinstance(value, str) and value.strip():
        return [item.strip() for item in value.split(",")]
    return []

def get_data_from_google_sheet(spreadsheet_name, sheet_name):
    """
    Fetches and processes data from a specific tab in a Google Sheet.

    It authenticates using credentials from the `GOOGLE_CREDENTIALS_JSON` environment
    variable (recommended for production) or falls back to a local `credenciales.json`
    file for development.

    Args:
        spreadsheet_name (str): The name of the Google Spreadsheet.
        sheet_name (str): The name of the sheet/tab to export.

    Returns:
        list: A list of dictionaries, where each dictionary represents a row.
        
    Raises:
        gspread.exceptions.SpreadsheetNotFound: If the spreadsheet is not found.
        gspread.exceptions.WorksheetNotFound: If the worksheet is not found.
        Exception: For other unexpected errors.
    """
    try:
        logging.info("Authenticating with Google Sheets API.")
        # Defines the scope of access for the application.
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

        # --- Authentication ---
        # The recommended way for production is to use an environment variable.
        google_creds_json_str = os.environ.get("GOOGLE_CREDENTIALS_JSON")
        if google_creds_json_str:
            logging.info("Found GOOGLE_CREDENTIALS_JSON env var. Authenticating from string.")
            creds_dict = json.loads(google_creds_json_str)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            # Fallback for local development: use the JSON file.
            logging.info("GOOGLE_CREDENTIALS_JSON env var not found. Falling back to 'credenciales.json' file.")
            creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
        
        client = gspread.authorize(creds)
        
        logging.info(f"Opening spreadsheet '{spreadsheet_name}' and worksheet '{sheet_name}'.")
        spreadsheet = client.open(spreadsheet_name)

        # --- Sheet-specific Configuration ---
        sheet_configs = {
            "default": {
                "columns": [
                    "artist", "title", "date_release", "genre", "subgenres", "mood", "compilations",
                    "country", "format", "duration", "tracks", "spotify_id", "spotify_link",
                    "spotify_code", "card_link", "image", "type", "label", "text"
                ],
                "list_fields": ["genre", "subgenres", "mood", "compilations", "format"]
            },
            "Descriptors": {
                "columns": ["type", "en", "es", "color"],
                "list_fields": []
            },
            "Genres": {
                "columns": [
                    "en", "es", "genre", "Derivados", "Relacionados",
                    "Descripción", "Año", "Origen", "Artistas", "Mood"
                ],
                "list_fields": []
            }
        }
        
        config = sheet_configs.get(sheet_name, sheet_configs["default"])
        columns_to_keep = config["columns"]
        list_fields = config["list_fields"]

        sheet = spreadsheet.worksheet(sheet_name)
        headers = sheet.row_values(1)
        logging.info(f"Actual headers in '{sheet_name}': {headers}")
        
        header_counts = Counter(headers)
        duplicates = [h for h, c in header_counts.items() if c > 1]
        if duplicates:
            logging.warning(f"Duplicate header(s) found in sheet '{sheet_name}': {duplicates}. This may cause data to be overwritten.")
        
        records = sheet.get_all_records()
        processed_records = []
        
        logging.info(f"Processing {len(records)} records from the sheet.")
        for record in records:
            filtered_record = {col: record.get(col, "") for col in columns_to_keep}
            
            for field in list_fields:
                if field in filtered_record:
                    filtered_record[field] = to_list(filtered_record[field])

            processed_records.append(filtered_record)

        logging.info("Finished processing all records.")
        return processed_records

    except gspread.exceptions.SpreadsheetNotFound:
        logging.error(f"Spreadsheet '{spreadsheet_name}' not found or credentials do not grant permission.")
        raise
    except gspread.exceptions.WorksheetNotFound:
        logging.error(f"Worksheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'.")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while accessing Google Sheets: {e}", exc_info=True)
        raise
