import unittest
from unittest.mock import patch, MagicMock
from typing import Any, List, Dict
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_processes.load_data import LoadETL


class TestLoadETL(unittest.TestCase):
    """
    Unit tests for the LoadETL class.
    """

    @patch("data_processes.load_data.SQLiteDatabase")
    @patch("data_processes.load_data.load_queries_from_json")
    def test_run_load(
        self, mock_load_queries: MagicMock, mock_sqlite_db: MagicMock
    ) -> None:
        """
        Test run_load to ensure it loads data into SQLite correctly.
        """
        # Mock the query list
        mock_load_queries.return_value = [
            {"query": "CREATE TABLE ...", "params": []},
            {"query": "INSERT INTO ...", "params": []},
        ]

        # Mock the SQLiteDatabase instance
        mock_db_instance = MagicMock()
        mock_sqlite_db.return_value = mock_db_instance

        # Create an instance of LoadETL and run the load method
        loader = LoadETL(database_path="test.db", query_path="queries.json")
        loader.run_load([{"uri": "123", "text": "Valid post"}])

        # Assertions
        mock_db_instance.execute_query.assert_called()
        self.assertEqual(mock_db_instance.execute_query.call_count, 2)


if __name__ == "__main__":
    unittest.main()