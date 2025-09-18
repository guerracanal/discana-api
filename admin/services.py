import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from admin.google_sheets import get_data_from_google_sheet

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def dump_google_sheet_data_to_db(spreadsheet, sheet, collection_name):
    """
    Orchestrates fetching data from Google Sheets and loading it into a MongoDB collection.

    Args:
        spreadsheet (str): The name of the Google Spreadsheet.
        sheet (str): The name of the worksheet.
        collection_name (str): The name of the MongoDB collection to update.

    Returns:
        int: The number of records successfully inserted into the database.
    
    Raises:
        ValueError: If the MONGO_SRV environment variable is not set.
        ConnectionFailure: If a connection to MongoDB cannot be established.
        Exception: For errors during data fetching or database operations.
    """
    # 1. Fetch data from Google Sheets
    # This function is now responsible for its own error handling and logging.
    logging.info(f"Starting data dump from Google Sheet '{sheet}' to collection '{collection_name}'.")
    records = get_data_from_google_sheet(spreadsheet, sheet)

    if not records:
        logging.warning("No records were fetched from Google Sheets. Nothing to insert.")
        return 0

    # 2. Connect to MongoDB
    mongo_srv = os.environ.get("MONGO_SRV")
    if not mongo_srv:
        logging.error("MONGO_SRV environment variable is not set.")
        raise ValueError("MONGO_SRV environment variable must be set to connect to the database.")

    client = None  # Initialize client to None to ensure it can be closed in a finally block
    try:
        logging.info("Connecting to MongoDB...")
        client = MongoClient(mongo_srv, serverSelectionTimeoutMS=5000) # Set a timeout
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        logging.info("Successfully connected to MongoDB.")
        
        db = client.get_default_database() 
        collection = db[collection_name]

        # 3. Update MongoDB collection
        # Using a transactional approach: first clear the collection, then insert new data.
        logging.info(f"Clearing all documents from collection '{collection_name}'.")
        collection.delete_many({})
        
        logging.info(f"Inserting {len(records)} new records into collection '{collection_name}'.")
        result = collection.insert_many(records)
        
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
        # Ensure the connection is closed even if errors occur.
        if client:
            client.close()
            logging.info("MongoDB connection closed.")
