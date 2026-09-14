import pytest
from calculator import Calculator


@pytest.fixture
def calc():
    """Fixture that auto-creates calc instance for tests"""
    return Calculator()




def test_add(calc):
    assert calc.add(2, 3) == 5
    assert calc.add(-1, 1) == 0
    assert calc.add(0, 0) == 0
    assert calc.add(-5, -3) == -8


def test_subtract(calc):
    assert calc.subtract(5, 3) == 2
    assert calc.subtract(0, 5) == -5
    assert calc.subtract(-2, -3) == 1
    assert calc.subtract(10, 0) == 10


def test_multiply(calc):
    assert calc.multiply(2, 3) == 6
    assert calc.multiply(-2, 3) == -6
    assert calc.multiply(0, 5) == 0
    assert calc.multiply(-2, -3) == 6


def test_divide(calc):
    assert calc.divide(6, 3) == 2
    assert calc.divide(5, 2) == 2.5
    assert calc.divide(-6, 3) == -2
    assert calc.divide(0, 5) == 0


def test_mod(calc):
    assert calc.mod(10, 3) == 1
    assert calc.mod(7, 2) == 1
    assert calc.mod(0, 5) == 0
    assert calc.mod(-10, 3) == 2  



def test_divide_by_zero(calc):
    with pytest.raises(ZeroDivisionError):
        calc.divide(5, 0)


def test_mod_by_zero(calc):
    with pytest.raises(ZeroDivisionError):
        calc.mod(5, 0)
