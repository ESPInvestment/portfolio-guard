import unittest
from datetime import date
from tools.validate_prices import validate

class CSVValidationTests(unittest.TestCase):
    def test_valid(self):
        rows, errors = validate("isin,date,price,source\nDE0009770206,2026-11-13,101.23,Manual NAV\n", date(2026, 11, 16))
        self.assertEqual(len(rows), 1)
        self.assertFalse(errors)

    def test_reject_unknown_isin(self):
        rows, errors = validate("isin,date,price,source\nUS0000000000,2026-11-13,101.23,Manual\n", date(2026, 11, 16))
        self.assertFalse(rows)
        self.assertTrue(errors)

    def test_reject_duplicate_dates(self):
        rows, errors = validate("isin,date,price,source\nDE0009770206,2026-11-13,100,Manual\nDE0009770206,2026-11-13,101,Manual\n", date(2026, 11, 16))
        self.assertEqual(len(rows), 1)
        self.assertTrue(errors)

    def test_reject_future_and_bad_prices(self):
        rows, errors = validate("isin,date,price,source\nDE0009770206,2026-11-17,100,Manual\nFR0010524777,2026-11-13,-4,Manual\n", date(2026, 11, 16))
        self.assertFalse(rows)
        self.assertEqual(len(errors), 2)

if __name__ == "__main__":
    unittest.main()
