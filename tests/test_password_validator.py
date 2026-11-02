"""
Набор модульных тестов для функции validate_password.
"""

import unittest

from src.password_validator import validate_password


class TestPasswordValidator(unittest.TestCase):
    """Тесты валидатора пароля."""

    # ---------- 1. Позитивное тестирование ----------

    def test_valid_latin_password(self):
        self.assertTrue(validate_password("SecurePass1!"))

    def test_valid_cyrillic_password(self):
        self.assertTrue(validate_password("ПарольТест9#"))

    # ---------- 2. Граничные значения длины (BVA) ----------

    def test_boundary_length_7(self):
        # 7 символов: a + A + 1 + ! + ... ровно 7
        self.assertFalse(validate_password("Aa1!aaa"))

    def test_boundary_length_8(self):
        # 8 символов: нижняя граница
        self.assertTrue(validate_password("Aa1!aaaa"))

    def test_boundary_length_20(self):
        # 20 символов: верхняя граница
        self.assertTrue(validate_password("Aa1!" + "a" * 16))

    def test_boundary_length_21(self):
        # 21 символ: на 1 больше верхней границы
        self.assertFalse(validate_password("Aa1!" + "a" * 17))

    # ---------- 3. Классы эквивалентности ----------

    def test_missing_uppercase(self):
        self.assertFalse(validate_password("securepass1!"))

    def test_missing_lowercase(self):
        self.assertFalse(validate_password("SECUREPASS1!"))

    def test_missing_digit(self):
        self.assertFalse(validate_password("SecurePassword!"))

    def test_missing_special(self):
        self.assertFalse(validate_password("SecurePassword1"))

    def test_underscore_not_special(self):
        # '_' не входит в разрешённый перечень спецсимволов
        self.assertFalse(validate_password("SecurePass1_"))

    def test_question_mark_not_special(self):
        # '?' не входит в разрешённый перечень спецсимволов
        self.assertFalse(validate_password("SecurePass1?"))

    def test_empty_string(self):
        self.assertFalse(validate_password(""))

    # ---------- 4. Исключительные ситуации: ValueError ----------

    def test_space_inside_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_password("Pass 1234!")

    def test_space_at_start_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_password(" Pass1234!")

    def test_space_at_end_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_password("Pass1234! ")

    # ---------- 5. Исключительные ситуации: TypeError ----------

    def test_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            validate_password(None)

    def test_int_raises_type_error(self):
        with self.assertRaises(TypeError):
            validate_password(12345678)

    def test_float_raises_type_error(self):
        with self.assertRaises(TypeError):
            validate_password(12.5)

    def test_list_raises_type_error(self):
        with self.assertRaises(TypeError):
            validate_password(["P", "a", "s", "s", "1", "!"])

    def test_dict_raises_type_error(self):
        with self.assertRaises(TypeError):
            validate_password({"password": "SecurePass1!"})


if __name__ == "__main__":
    unittest.main()