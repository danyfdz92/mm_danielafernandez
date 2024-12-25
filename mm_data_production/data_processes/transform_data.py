"""
Script for transforming data.
"""

import logging
from typing import List, Dict

class TransformETL:
    """
    Transform ETL class responsible for cleaning data,
    removing blank rows, etc.
    """

    def __init__(self, columns_to_check: List[str]) -> None:
        """
        :param columns_to_check: A list of column names to check for blanks.
        """
        self.columns_to_check = columns_to_check

    def run_transform(self, data: List[Dict]) -> List[Dict]:
        """
        Remove rows that have blank or None values in any
        of the specified columns_to_check.

        :param data: The raw data as a list of dictionaries.
        :return: Cleaned list of dictionaries.
        """
        logging.info("Starting data transformation.")

        if not data:
            logging.warning("Input data is empty.")
            return []

        cleaned_data = []
        for row in data:
            # Only keep the row if ALL columns_to_check have non-blank values
            keep_row = True
            for col in self.columns_to_check:
                value = row.get(col)
                if value is None or str(value).strip() == '':
                    keep_row = False
                    break
            if keep_row:
                cleaned_data.append(row)

        logging.info(
            "Transformation complete. Number of records after cleaning: %d",
            len(cleaned_data)
        )
        return cleaned_data