import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")),
)

from triangles import solve

NAN_COORDS = [(-2, -2), (-2, -2), (-2, -2)]
INVALID_COORDS = [(-1, -1), (-1, -1), (-1, -1)]


def test_non_numeric_input_returns_empty_type_and_nan_coordinates():
    assert solve("abc", "2", "3") == ("", NAN_COORDS)


def test_nan_value_returns_empty_type_and_nan_coordinates():
    assert solve("nan", "1", "1") == ("", NAN_COORDS)


def test_infinite_side_is_not_triangle_and_invalid_coordinates():
    assert solve("inf", "1", "1") == ("Not a triangle", INVALID_COORDS)


def test_zero_side_is_not_triangle():
    assert solve("0", "1", "1") == ("Not a triangle", INVALID_COORDS)


def test_negative_side_is_not_triangle():
    assert solve("-1", "2", "3") == ("Not a triangle", INVALID_COORDS)


def test_triangle_inequality_violation_is_not_triangle():
    assert solve("1", "2", "10") == ("Not a triangle", INVALID_COORDS)


def test_equilateral_triangle_type_and_coordinates():
    tri_type, coords = solve("3", "3", "3")
    assert tri_type == "Equilateral (равносторонний)"
    assert coords == [(10, 90), (90, 90), (50, 21)]


def test_isosceles_triangle_type_has_no_leading_space():
    tri_type, coords = solve("3", "3", "4")
    assert tri_type == "Isosceles (равнобедренный)"
    assert coords == [(10, 90), (70, 90), (17, 30)]


def test_scalene_triangle_type_for_3_4_5():
    tri_type, coords = solve("3", "4", "5")
    assert tri_type == "Scalene (разносторонний)"
    assert coords == [(10, 90), (58, 90), (10, 26)]


def test_decimal_sides_are_supported():
    tri_type, _ = solve("1.5", "2.5", "3.0")
    assert tri_type == "Scalene (разносторонний)"


def test_isosceles_detected_when_equal_sides_are_not_first_two():
    tri_type, _ = solve("4", "3", "3")
    assert tri_type == "Isosceles (равнобедренный)"


def test_coordinates_are_inside_allowed_field():
    _, coords = solve("50", "50", "50")
    for x, y in coords:
        assert 0 <= x <= 100
        assert 0 <= y <= 100