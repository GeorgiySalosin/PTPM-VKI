# test_calculator.py
import pytest
from main import add, subtract, multiply, divide, mod


#   assert is equal to 

#   if not (multiply(2, 3) == 6):
#       raise AssertionError("assert multiply(2, 3) == 6")



def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
    assert add(-5, -3) == -8

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5
    assert subtract(-2, -3) == 1
    assert subtract(10, 0) == 10

def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(-2, 3) == -6
    assert multiply(0, 5) == 0
    assert multiply(-2, -3) == 6

def test_divide():
    assert divide(6, 3) == 2
    assert divide(5, 2) == 2.5
    assert divide(-6, 3) == -2
    assert divide(0, 5) == 0

def test_mod():
    assert mod(10, 3) == 1
    assert mod(7, 2) == 1
    assert mod(0, 5) == 0
    assert mod(-10, 3) == 2  # В Python остаток положительный

# Тест на деление на ноль (ожидаем ошибку)
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(5, 0)

# Тест на модуль от деления на ноль
def test_mod_by_zero():
    with pytest.raises(ZeroDivisionError):
        mod(5, 0)



# Параметризованные тесты (более продвинутый подход)
# @pytest.mark.parametrize("a, b, expected", [
#     (2, 3, 5),
#     (-1, 1, 0),
#     (0, 0, 0),
#     (100, 200, 300),
# ])
# def test_add_parametrized(a, b, expected):
#     assert add(a, b) == expected



# @pytest.mark.parametrize("a, b, expected", [
#     (10, 3, 1),
#     (7, 2, 1),
#     (0, 5, 0),
#     (8, 4, 0),
# ])
# def test_mod_parametrized(a, b, expected):
#     assert mod(a, b) == expected

# # Тестирование с плавающей точкой (с учетом погрешности)
# def test_divide_float():
#     assert divide(1, 3) == pytest.approx(0.3333333333333333)
#     assert divide(2, 3) == pytest.approx(0.6666666666666666, rel=1e-6)

# # Фикстура для повторяющихся данных (если нужно)
# @pytest.fixture
# def sample_numbers():
#     return [(2, 3, 5), (-1, 1, 0), (0, 0, 0)]

# def test_add_with_fixture(sample_numbers):
#     for a, b, expected in sample_numbers:
#         assert add(a, b) == expected