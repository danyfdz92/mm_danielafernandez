import unittest
from unittest.mock import patch, MagicMock, mock_open
from typing import Any, List
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_admin.sqlite_manager import SQLiteDatabase, load_queries_from_json

class TestSQLiteManager(unittest.TestCase):
    """
    Unit tests for the SQLiteManager class and associated functions.
    """

    @patch("database_admin.sqlite_manager.sqlite3.connect")
    def test_execute_query(self, mock_connect: MagicMock) -> None:
        """
        Test execute_query to ensure it executes SQL queries correctly.
        """
        # Mock connection and cursor
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # Test the execute_query method
        db = SQLiteDatabase("test.db")
        db.execute_query("SELECT * FROM test")

        # Assertions
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test", ())
        mock_conn.commit.assert_called_once()

    @patch("builtins.open", new_callable=mock_open, read_data='[{"query": "SELECT * FROM test", "params": []}]')
    def test_load_queries_from_json(self, mock_file: MagicMock) -> None:
        """
        Test load_queries_from_json to ensure it correctly parses valid JSON.
        """
        # Run the function
        result: List[Any] = load_queries_from_json("queries.json")

        # Assertions
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["query"], "SELECT * FROM test")
        self.assertEqual(result[0]["params"], [])

        # Ensure the file was opened correctly
        mock_file.assert_called_once_with("queries.json", "r")


if __name__ == "__main__":
    unittest.main()