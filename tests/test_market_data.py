import unittest

from jsonl_stream_utils import normalize_bar, validate_bar, valid_bars


VALID = {
    "symbol": "000001.SZ",
    "timestamp": "2026-08-16T09:31:00+08:00",
    "open": 10.0,
    "high": 10.4,
    "low": 9.8,
    "close": 10.2,
    "volume": 120000,
}


class MarketDataTests(unittest.TestCase):
    def test_accepts_valid_bar(self):
        self.assertEqual(validate_bar(VALID), [])

    def test_reports_missing_and_invalid_values(self):
        row = {"symbol": "000001.SZ", "timestamp": "t", "open": "10"}
        errors = validate_bar(row)
        self.assertIn("missing field: close", errors)
        self.assertIn("missing field: volume", errors)

    def test_filters_invalid_bars(self):
        invalid = dict(VALID, high=9.0)
        self.assertEqual(valid_bars([VALID, invalid]), [VALID])

    def test_normalizes_numeric_types(self):
        normalized = normalize_bar(dict(VALID, open=10, volume=120000))
        self.assertEqual(normalized["symbol"], "000001.SZ")
        self.assertIsInstance(normalized["open"], float)
        self.assertIsInstance(normalized["volume"], float)

    def test_normalize_rejects_invalid_bar(self):
        with self.assertRaises(ValueError):
            normalize_bar(dict(VALID, low=11.0))


if __name__ == "__main__":
    unittest.main()
