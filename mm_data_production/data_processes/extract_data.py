"""
Script for extracting data from a HuggingFace dataset.
"""

import logging
from typing import List, Dict
from datasets import load_dataset

class ExtractETL:
    """
    Extract ETL class responsible for fetching data.
    """

    def __init__(self, dataset_url: str) -> None:
        """
        :param dataset_url: The HuggingFace dataset identifier
                            or a valid dataset path/URL.
        """
        self.dataset_url = dataset_url

    def run_extract(self) -> List[Dict]:
        """
        Extract the data from the HuggingFace dataset.
        Returns a list of dictionaries.
        """
        logging.info(
            "Starting extraction from HuggingFace dataset '%s'.", 
            self.dataset_url
        )

        try:
            dataset = load_dataset(self.dataset_url,  split="train")
            data_list = dataset.to_pandas().to_dict(orient='records')
            logging.info(
                "Extraction successful. Number of records extracted: %d", 
                len(data_list)
            )
            return data_list
        except Exception as e:
            logging.error("Error occurred during extraction: %s", e)
            raise