import unittest

from converter import Converter


class TestConverter(unittest.TestCase):
    def test_upper_range_returns_1000(self):
        for x in (100.7, 100.8, 101.0, 999.9, 1000.0):
            with self.subTest(x=x):
                result = Converter.do(x)
                self.assertEqual(result, 1000)
                self.assertIsInstance(result, int)

    def test_positive_range_returns_int_part(self):
        cases = [
            (0.1, 0),
            (0.9, 0),
            (1.0, 1),
            (65.7, 65),
            (99.9, 99),
            (100.6, 100),
        ]

        for x, expected in cases:
            with self.subTest(x=x):
                result = Converter.do(x)
                self.assertEqual(result, expected)
                self.assertIsInstance(result, int)

    def test_zero_raises_value_error(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)

        # -0.0 в Python равен 0.0
        with self.assertRaises(ValueError):
            Converter.do(-0.0)

    def test_negative_range_returns_int_part_minus_5(self):
        cases = [
            (-0.1, -5),   # int(-0.1) == 0
            (-0.9, -5),
            (-1.0, -6),
            (-1.5, -6),
            (-15.7, -20), # int(-15.7) == -15, -15 - 5 = -20
            (-30.5, -35), # граница диапазона [-30.5; 0)
            (-30.4, -35), # по порядку условий попадает в [-30.5; 0)
        ]

        for x, expected in cases:
            with self.subTest(x=x):
                result = Converter.do(x)
                self.assertEqual(result, expected)
                self.assertIsInstance(result, int)

    def test_lower_range_returns_minus_2000(self):
        for x in (-30.6, -31.0, -94.5, -1000.0):
            with self.subTest(x=x):
                result = Converter.do(x)
                self.assertEqual(result, -2000)
                self.assertIsInstance(result, int)


if __name__ == "__main__":
    unittest.main()