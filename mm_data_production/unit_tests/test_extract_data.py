import unittest
from unittest.mock import patch, MagicMock
from typing import Any, List, Dict
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_processes.extract_data import ExtractETL


class TestExtractETL(unittest.TestCase):
    """
    Unit tests for the ExtractETL class.
    """

    @patch("data_processes.extract_data.load_dataset")
    def test_run_extract(self, mock_load_dataset: MagicMock) -> None:
        """
        Test run_extract to ensure it fetches data correctly from HuggingFace datasets.
        """
        # Mock HuggingFace dataset
        mock_dataset = MagicMock()
        mock_dataset.to_pandas.return_value.to_dict.return_value = [
            {"uri": "123", "text": "sample post"}
        ]
        mock_load_dataset.return_value = mock_dataset

        # Create an instance of ExtractETL
        extractor = ExtractETL(dataset_url="alpindale/two-million-bluesky-posts")

        # Run the extract method
        result: List[Dict[str, Any]] = extractor.run_extract()

        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["uri"], "123")
        self.assertEqual(result[0]["text"], "sample post")

        # Ensure the HuggingFace dataset loader was called
        mock_load_dataset.assert_called_once_with(
            "alpindale/two-million-bluesky-posts", split="train"
        )


if __name__ == "__main__":
    unittest.main()