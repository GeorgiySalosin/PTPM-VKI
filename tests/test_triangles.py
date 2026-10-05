import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")),
)

from triangles import solve

NAN_COORDS = [(-2, -2), (-2, -2), (-2, -2)]
INVALID_COORDS = [(-1, -1), (-1, -1), (-1, -1)]


class TestTrianglesInvalidInput(unittest.TestCase):
    """NaN, inf и нечисловой ввод."""

    def test_non_numeric_input_returns_empty_type_and_nan_coordinates(self):
        self.assertEqual(solve("abc", "2", "3"), ("", NAN_COORDS))

    def test_nan_value_returns_empty_type_and_nan_coordinates(self):
        self.assertEqual(solve("nan", "1", "1"), ("", NAN_COORDS))

    def test_infinite_side_is_not_triangle_and_invalid_coordinates(self):
        self.assertEqual(
            solve("inf", "1", "1"),
            ("Not a triangle", INVALID_COORDS),
        )

    def test_zero_side_is_not_triangle(self):
        self.assertEqual(
            solve("0", "1", "1"),
            ("Not a triangle", INVALID_COORDS),
        )

    def test_negative_side_is_not_triangle(self):
        self.assertEqual(
            solve("-1", "2", "3"),
            ("Not a triangle", INVALID_COORDS),
        )

    def test_triangle_inequality_violation_is_not_triangle(self):
        self.assertEqual(
            solve("1", "2", "10"),
            ("Not a triangle", INVALID_COORDS),
        )


class TestTrianglesTypeAndCoordinates(unittest.TestCase):
    """Валидные треугольники: тип и координаты."""

    def test_equilateral_triangle_type_and_coordinates(self):
        tri_type, coords = solve("3", "3", "3")
        self.assertEqual(tri_type, "Equilateral (равносторонний)")
        self.assertEqual(coords, [(10, 90), (90, 90), (50, 21)])

    def test_isosceles_triangle_type_has_no_leading_space(self):
        tri_type, coords = solve("3", "3", "4")
        self.assertEqual(tri_type, "Isosceles (равнобедренный)")
        self.assertEqual(coords, [(10, 90), (70, 90), (17, 30)])

    def test_scalene_triangle_type_for_3_4_5(self):
        tri_type, coords = solve("3", "4", "5")
        self.assertEqual(tri_type, "Scalene (разносторонний)")
        self.assertEqual(coords, [(10, 90), (58, 90), (10, 26)])

    def test_decimal_sides_are_supported(self):
        tri_type, _ = solve("1.5", "2.5", "3.0")
        self.assertEqual(tri_type, "Scalene (разносторонний)")

    def test_isosceles_detected_when_equal_sides_are_not_first_two(self):
        tri_type, _ = solve("4", "3", "3")
        self.assertEqual(tri_type, "Isosceles (равнобедренный)")

    def test_coordinates_are_inside_allowed_field(self):
        _, coords = solve("50", "50", "50")
        for x, y in coords:
            self.assertGreaterEqual(x, 0)
            self.assertLessEqual(x, 100)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(y, 100)


if __name__ == "__main__":
    unittest.main()