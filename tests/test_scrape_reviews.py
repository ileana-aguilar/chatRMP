import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from unittest.mock import MagicMock, patch
from scrape_reviews import scrape_professor_reviews




class TestScraper(unittest.TestCase):
    @patch("scrape_reviews.driver")
    def test_scrape_reviews_mocked(self, mock_driver):
        mock_driver.get.return_value = None
        scrape_professor_reviews("12345", "Test Professor")
        
        mock_driver.get.assert_called_with("https://www.ratemyprofessors.com/professor/12345")

if __name__ == "__main__":
    unittest.main()
