import sqlite3
import json
import logging
import argparse
import os
from typing import List, Dict, Any, Union
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

class SQLiteDatabase:
    """Handles SQL operations (both DDL and DML) on an SQLite database."""

    def __init__(self, db_name: str):
        """
        Initialize the SQLite database connection.

        :param db_name: The name of the SQLite database file.
        """
        logging.info(f"Initializing the SQLite database connection")
        self.db_name = db_name
        self.connection = None

    def _connect(self) -> sqlite3.Connection:
        """
        Connect to the SQLite database.

        :return: A connection object for the SQLite database.
        """
        # Define the full path for the database_files folder
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory of the script
        database_dir = os.path.join(script_dir, "database_files")

        # Create the folder if it does not exist
        if not os.path.exists(database_dir):
            os.makedirs(database_dir)
            logging.info(f"Created directory: {database_dir}")

        # Construct the full database file path
        db_path = os.path.join(database_dir, self.db_name)

        if self.connection is None:
            self.connection = sqlite3.connect(db_path)
            logging.info(f"Connected to the database {self.db_name}.")
        return self.connection

    def execute_query(self, query: str, params: Union[tuple, list] = ()) -> Union[List[Any], None]:
        """
        Execute a single SQL query.

        :param query: SQL query string to be executed.
        :param params: Optional parameters to pass with the query.
        :return: Rows for `SELECT` queries; None for others.
        """
        conn = self._connect()
        cursor = conn.cursor()
        try:
            logging.info(f"Executing query: {query} with params: {params}")
            cursor.execute(query, params)
            
            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                logging.info(f"Query returned {len(rows)} rows.")
                conn.commit()
                return rows
            else:
                conn.commit()
                logging.info("Query executed successfully.")
        except sqlite3.Error as e:
            logging.error(f"Error executing query: {query} with params: {params}. Error: {e}")
            conn.rollback()

    def execute_queries(self, queries: List[Dict[str, Any]]) -> None:
        """
        Execute multiple queries sequentially.

        :param queries: A list of dictionaries containing 'query' and 'params'.
        """

        for query_dict in queries:
            query = query_dict.get("query")
            params = query_dict.get("params", [])
            if not query:
                logging.warning("Skipping entry without a valid 'query' key.")
                continue
            else:
                result = self.execute_query(query, tuple(params))
                if result is not None:
                    logging.info(f"Result: {result}")

    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed.")


def load_queries_from_json(json_file: str) -> List[Dict[str, Any]]:
    """
    Load SQL queries from a JSON file.

    :param json_file: Path to the JSON file containing SQL queries.
    :return: List of queries as dictionaries.
    """
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
        logging.info(f"Loaded {len(data)} queries from '{json_file}'.")
        return data
    except FileNotFoundError:
        logging.error(f"The file '{json_file}' was not found.")
        raise
    except json.JSONDecodeError:
        logging.error(f"Failed to parse the JSON file '{json_file}'. Please check its format.")
        raise

def run_queries_from_json(db_name: str, queries_json_file: str) -> None:
    """
    Main function to execute queries on a database.

    :param db_name: The SQLite database file.
    :param queries_json_file: Path to the JSON file containing queries.
    """
    logging.info(f"Reading queries from: {queries_json_file}, running on database {db_name}")

    db = None

    try:
        queries = load_queries_from_json(queries_json_file)
        db = SQLiteDatabase(db_name)
        db.execute_queries(queries)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        if db:
            db.close()


def main() -> None:
    """
    Main function to handle command-line arguments and execute SQL queries.

    :param args: Arguments passed from the command line.
    """
    
    # Create the parser
    parser = argparse.ArgumentParser(
        description="SQLite Manager. Example usage: python sqlite_manager.py -db test.db -qf queries.json"
    )   

    # Add the arguments
    parser.add_argument('-db', '--db_name', type=str, help="Name of the SQLite database file", required=True)
    parser.add_argument('-qf', '--queries_json_file', type=str, help="Location of the queries file", required=True)

    # Parse the arguments
    args = parser.parse_args()

    # Access the values
    db_name = args.db_name
    queries_json_file = args.queries_json_file
    
    logging.info(f"Reading queries from: {queries_json_file}, running on database {db_name}")

    run_queries_from_json(db_name, queries_json_file)

if __name__ == "__main__":
    main()
