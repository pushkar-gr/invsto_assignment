import unittest
import requests
import json
import os

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# default parameters
if DB_HOST == None:
    DB_HOST = "localhost"

if DB_PORT == None:
    DB_PORT = "8000"

BASE_URL = "httl://{host}:{port}".format(
    host=DB_HOST,
    port=DB_PORT,
)


class TestMovingAverageCalculations(unittest.TestCase):
    # test correctness of moving average calculations
    def test_correct_moving_averages(self):
        data = [
            {
                "datetime": "2025-04-28T06:00:38.503Z",
                "open": 100.5,
                "high": 102.0,
                "low": 98.0,
                "close": 100,
                "volume": 1000,
                "instrument": "AAPL",
            },
            {
                "datetime": "2025-04-28T06:01:38.503Z",
                "open": 103.0,
                "high": 106.0,
                "low": 100.0,
                "close": 105,
                "volume": 900,
                "instrument": "AAPL",
            },
            {
                "datetime": "2025-04-28T06:02:38.503Z",
                "open": 104.0,
                "high": 105.0,
                "low": 101.0,
                "close": 102,
                "volume": 950,
                "instrument": "AAPL",
            },
            {
                "datetime": "2025-04-28T06:03:38.503Z",
                "open": 107.0,
                "high": 109.0,
                "low": 106.0,
                "close": 108,
                "volume": 1100,
                "instrument": "AAPL",
            },
            {
                "datetime": "2025-04-28T06:04:38.503Z",
                "open": 109.0,
                "high": 112.0,
                "low": 108.0,
                "close": 110,
                "volume": 1200,
                "instrument": "AAPL",
            },
        ]

        # post each record to the /data endpoint
        for record in data:
            requests.post(BASE_URL + "/data", json=record)

        response = requests.get(BASE_URL + "/strategy/performance")
        self.assertEqual(response.status_code, 200)
        performance = response.json()

        # check if calculated moving averages are correct
        short_term_avg = (108 + 110) / 2
        long_term_avg = (100 + 105 + 102 + 108 + 110) / 5

        self.assertAlmostEqual(
            performance.get("short_term_avg", 0), short_term_avg, places=2
        )
        self.assertAlmostEqual(
            performance.get("long_term_avg", 0), long_term_avg, places=2
        )

    # test buy/sell signals generation
    def test_buy_sell_signals(self):
        response = requests.get(BASE_URL + "/strategy/performance")
        self.assertEqual(response.status_code, 200)

        try:
            performance = response.json()
        except json.JSONDecodeError:
            self.fail("Response is not valid JSON")

        # ensure buy/sell signals are generated properly
        self.assertIn("buy_signals", performance)
        self.assertIn("sell_signals", performance)


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
    test_cases = [TestMovingAverageCalculations, TestDataInputValidation]
    suite = unittest.TestSuite()
    for test_case in test_cases:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test_case))
    unittest.TextTestRunner(verbosity=2).run(suite)
