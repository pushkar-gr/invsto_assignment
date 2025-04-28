import unittest
import requests
import json

BASE_URL = "http://host.docker.internal:8000"


class TestDataInputValidation(unittest.TestCase):
    # test valid data input
    def test_valid_data(self):
        body = {
            "datetime": "2025-04-28T06:00:38.503Z",
            "open": 100.5,
            "high": 105.3,
            "low": 99.1,
            "close": 102.4,
            "volume": 500,
            "instrument": "AAPL",
        }
        response = requests.post(BASE_URL + "/data", json=body)
        self.assertEqual(response.status_code, 200)

    # test invalid datetime format
    def test_invalid_datetime(self):
        body = {
            "datetime": "28-04-2025 06:00:38",  # invalid datetime format
            "open": 100.5,
            "high": 105.3,
            "low": 99.1,
            "close": 102.4,
            "volume": 500,
            "instrument": "AAPL",
        }
        response = requests.post(BASE_URL + "/data", json=body)
        self.assertTrue(response.status_code > 200)

    # test missing required field
    def test_missing_field(self):
        body = {
            "datetime": "2025-04-28T06:00:38.503Z",
            "open": 100.5,
            "high": 105.3,
            "low": 99.1,
            "close": 102.4,
        }
        response = requests.post(BASE_URL + "/data", json=body)
        self.assertTrue(response.status_code > 200)

    # test invalid volume type
    def test_invalid_volume_type(self):
        body = {
            "datetime": "2025-04-28T06:00:38.503Z",
            "open": 100.5,
            "high": 105.3,
            "low": 99.1,
            "close": 102.4,
            "volume": "five hundred",  # invalid type for volume
            "instrument": "AAPL",
        }
        response = requests.post(BASE_URL + "/data", json=body)
        self.assertTrue(response.status_code > 200)



if __name__ == "__main__":
    unittest.main(verbosity=2)
