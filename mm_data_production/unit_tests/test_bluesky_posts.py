import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
from typing import Any

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

        # Test case
        db = SQLiteDatabase("test.db")
        db.execute_query("SELECT * FROM test")

        # Assertions
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test", ())
        mock_conn.commit.assert_called_once()

    @patch("builtins.open", new_callable=mock_open, read_data='[{"query": "SELECT * FROM test", "params": []}]')
    def test_load_queries_from_json(self, mock_file: MagicMock) -> None:
        """
        Test load_queries_from_json to ensure it correctly parses JSON data.
        """
        result = load_queries_from_json("queries.json")

        # Assertions
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["query"], "SELECT * FROM test")
        self.assertEqual(result[0]["params"], [])

        # Ensure the file was opened with the correct arguments
        mock_file.assert_called_once_with("queries.json", "r")

    @patch("database_admin.sqlite_manager.sqlite3.connect")
    def test_execute_query_with_params(self, mock_connect: MagicMock) -> None:
        """
        Test execute_query with SQL parameters.
        """
        # Mock connection and cursor
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # Test case
        db = SQLiteDatabase("test.db")
        db.execute_query("INSERT INTO test (id, name) VALUES (?, ?)", params=(1, "John"))

        # Assertions
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO test (id, name) VALUES (?, ?)", (1, "John")
        )
        mock_conn.commit.assert_called_once()



if __name__ == "__main__":
    unittest.main()