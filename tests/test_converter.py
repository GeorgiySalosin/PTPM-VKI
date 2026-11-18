import unittest
import sys, os

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")),
)

from converter import Converter


class TestConverterZeroInput(unittest.TestCase):
    """x == 0.0 — единственный вход, который должен падать по значению."""

    def test_positive_zero_raises_value_error(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    def test_negative_zero_raises_value_error(self):
        with self.assertRaises(ValueError):
            Converter.do(-0.0)


class TestConverterUpperRange(unittest.TestCase):
    """x ∈ [100.7; +∞) → 1000."""

    def test_left_boundary_returns_1000(self):
        self.assertEqual(Converter.do(100.7), 1000)

    def test_above_boundary_returns_1000(self):
        for x in (100.8, 101.0, 999.9, 10000.0, 1e6):
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), 1000)

    def test_returns_int_type(self):
        self.assertIsInstance(Converter.do(100.7), int)


class TestConverterPositiveRange(unittest.TestCase):
    """x ∈ (0; 100.7) → int(x)."""

    def test_values_less_than_one_return_zero(self):
        for x in (0.1, 0.5, 0.9):
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), 0)

    def test_values_greater_than_one_return_integer_part(self):
        for x, expected in ((1.0, 1), (65.7, 65), (99.9, 99)):
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), expected)

    def test_right_boundary_minus_one_tenth_returns_100(self):
        # 100.6 — максимальное значение, попадающее в (0; 100.7)
        self.assertEqual(Converter.do(100.6), 100)

    def test_returns_int_type(self):
        self.assertIsInstance(Converter.do(65.7), int)


class TestConverterNegativeRange(unittest.TestCase):
    """x ∈ [-30.4; 0) → int(x) - 5."""

    def test_upper_boundary_minus_one_tenth(self):
        self.assertEqual(Converter.do(-0.1), -5)

    def test_upper_boundary_minus_nine_tenths(self):
        self.assertEqual(Converter.do(-0.9), -5)

    def test_negative_integer_minus_5(self):
        self.assertEqual(Converter.do(-1.0), -6)

    def test_negative_fractional_minus_5(self):
        self.assertEqual(Converter.do(-15.7), -20)

    def test_left_boundary_minus_30_4(self):        # -30.4 ЗДЕСЬ
        self.assertEqual(Converter.do(-30.4), -35)

    def test_returns_int_type(self):
        self.assertIsInstance(Converter.do(-15.7), int)


class TestConverterLowerRange(unittest.TestCase):
    """x ∈ (-∞; -30.5] → -2000."""

    def test_below_boundary_returns_minus_2000(self):
        for x in (-30.6, -31.0, -94.5, -1000.0, -1e6):
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), -2000)

    def test_right_boundary_minus_30_5_returns_minus_2000(self):    # -30.5 теперь входит в этот диапазон
        self.assertEqual(Converter.do(-30.5), -2000)

    def test_returns_int_type(self):
        self.assertIsInstance(Converter.do(-94.5), int)


class TestConverterInvalidPrecision(unittest.TestCase):
    """Ввод с более чем одним знаком после запятой."""

    def test_two_decimal_places_raise_value_error(self):
        for x in (65.75, -30.45, 0.25, 100.75, -0.15, 99.99):
            with self.subTest(x=x):
                with self.assertRaises(ValueError):
                    Converter.do(x)

    def test_many_decimal_places_raise_value_error(self):
        for x in (1.23456, -0.001, 3.14159, -99.999):
            with self.subTest(x=x):
                with self.assertRaises(ValueError):
                    Converter.do(x)

    def test_single_decimal_place_passes_precision_check(self):
        # Контрпроверка
        for x in (0.1, 65.7, 100.7, -0.1, -30.5, -94.5):
            with self.subTest(x=x):
                Converter.do(x)

if __name__ == "__main__":
    unittest.main()