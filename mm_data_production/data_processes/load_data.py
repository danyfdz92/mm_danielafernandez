"""
Script for loading data into SQLite database.
"""

import logging
from typing import List, Dict
from database_admin.sqlite_manager import SQLiteDatabase  # To manage sqlite operations
from database_admin.sqlite_manager import load_queries_from_json  # Run list of queries from json file

class LoadETL:
    """
    Load ETL class responsible for loading data into SQLite database.
    """

    def __init__(self, database_path: str, query_path: str) -> None:
        self.database_path = database_path
        self.query_path = query_path

    def run_load(self, data: List[Dict]) -> None:
        """
        Load data into the specified SQLite database using the existing SQLiteDatabase class.
        """
        logging.info("Starting data load into SQLite database at '%s'.", self.database_path)

        if not data:
            logging.warning("No data to load.")
            return

        db = SQLiteDatabase(self.database_path)
        try:
            # Running queries
            
            query_list = load_queries_from_json(self.query_path)
            
            db.execute_query(query_list[0]["query"]) # Create table if it does not exist

            # Simple insertion for demonstration
            insert_query = query_list[1] # Get upsert statement
            for row in data:
                # Get keys as a list
                values = list(row.values())
                db.execute_query(insert_query["query"], values)
                break

            logging.info("Data load complete. Number of records inserted: %d", len(data))
        except Exception as e:
            logging.error("Error occurred during load: %s", e)
            raise
        finally:
            db.close()