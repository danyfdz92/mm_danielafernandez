import unittest
from typing import List, Dict, Any
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_processes.transform_data import TransformETL

class TestTransformETL(unittest.TestCase):
    """
    Unit tests for the TransformETL class.
    """

    def test_run_transform(self) -> None:
        """
        Test run_transform to ensure it removes rows with missing or blank values.
        """
        transformer = TransformETL(columns_to_check=["uri", "created_at"])
        raw_data: List[Dict[str, Any]] = [
            {"uri": "123", "created_at": "2024-12-01", "text": "Valid post"},
            {"uri": None, "created_at": "2024-12-01", "text": "Invalid post"},
        ]

        result: List[Dict[str, Any]] = transformer.run_transform(raw_data)

        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["uri"], "123")
        self.assertEqual(result[0]["text"], "Valid post")


if __name__ == "__main__":
    unittest.main()