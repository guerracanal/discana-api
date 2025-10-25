import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from admin.google_sheets import get_data_from_google_sheet

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def dump_google_sheet_data_to_db(spreadsheet, sheets, collection_name, overwrite=False):
    """
    Orchestrates fetching data from Google Sheets and loading it into a MongoDB collection.
    Can process multiple sheets and optionally overwrite the destination collection.

    Args:
        spreadsheet (str): The name of the Google Spreadsheet.
        sheets (list): A list of worksheet names to process.
        collection_name (str): The name of the MongoDB collection to update.
        overwrite (bool): If True, the existing collection will be cleared before inserting new data.

    Returns:
        int: The number of records successfully inserted into the database.
    
    Raises:
        ValueError: If required environment variables are not set or parameters are invalid.
        ConnectionFailure: If a connection to MongoDB cannot be established.
        Exception: For errors during data fetching or database operations.
    """
    if not isinstance(sheets, list) or not sheets:
        raise ValueError("'sheets' must be a non-empty list of sheet names.")

    # 1. Fetch data from all specified Google Sheets
    all_records = []
    logging.info(f"Starting data dump from Google Spreadsheet '{spreadsheet}' to collection '{collection_name}'.")
    for sheet in sheets:
        logging.info(f"Fetching data from sheet: '{sheet}'...")
        try:
            records = get_data_from_google_sheet(spreadsheet, sheet)
            if records:
                all_records.extend(records)
                logging.info(f"Successfully fetched {len(records)} records from sheet '{sheet}'.")
            else:
                logging.warning(f"No records were fetched from sheet '{sheet}'.")
        except Exception as e:
            logging.error(f"Failed to fetch data from sheet '{sheet}': {e}")
            # For now, we'll log the error and continue with other sheets.
            pass

    if not all_records:
        logging.warning("No records were fetched from any of the specified sheets. Nothing to insert.")
        return 0

    # 2. Connect to MongoDB
    MONGO_URI = os.environ.get("MONGO_URI")
    if not MONGO_URI:
        logging.error("MONGO_URI environment variable is not set.")
        raise ValueError("MONGO_URI environment variable must be set to connect to the database.")

    client = None
    try:
        logging.info("Connecting to MongoDB...")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ismaster')
        logging.info("Successfully connected to MongoDB.")
        
        db = client.get_default_database() 
        collection = db[collection_name]

        # 3. Handle overwrite logic
        if overwrite:
            logging.info(f"Overwrite flag is set. Clearing all documents from collection '{collection_name}'.")
            collection.delete_many({})
        
        # 4. Update MongoDB collection
        logging.info(f"Inserting {len(all_records)} new records into collection '{collection_name}'.")
        result = collection.insert_many(all_records)
        
        records_inserted = len(result.inserted_ids)
        logging.info(f"Successfully inserted {records_inserted} documents.")
        
        return records_inserted

    except ConnectionFailure as e:
        logging.error(f"Could not connect to MongoDB: {e}", exc_info=True)
        raise
    except OperationFailure as e:
        logging.error(f"A database operation failed: {e}", exc_info=True)
        raise
    finally:
        if client:
            client.close()
            logging.info("MongoDB connection closed.")
