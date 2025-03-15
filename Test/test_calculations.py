# tests/test_calculations.py
import unittest
from calculations import calculate_footprint, calculate_offset

class TestCalculations(unittest.TestCase):
    def test_calculate_footprint(self):
        result = calculate_footprint(100, 50, 30, 10, 50, 1000, 8)
        self.assertAlmostEqual(result, 1234.56, places=2)

    def test_calculate_offset(self):
        result = calculate_offset(1000)
        self.assertAlmostEqual(result, 45.93, places=2)

if __name__ == "__main__":
    unittest.main()