import os
import sys
import tempfile
import unittest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")),
)

from database import TriangleDatabase
from notifier import EmailNotifier
from triangles_controller import TriangleController
from user_interface import ConsoleUserInterface


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS triangles (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    side_a         REAL NOT NULL,
    side_b         REAL NOT NULL,
    side_c         REAL NOT NULL,
    triangle_type  TEXT,
    error_message  TEXT,
    UNIQUE (side_a, side_b, side_c)
);
"""


# ---------- database.py: 56-58 (except IntegrityError), 111-119 (delete) ----------

class DatabaseCoverageTests(unittest.TestCase):

    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.db = TriangleDatabase(self.path)
        self.db.connection.executescript(SCHEMA_SQL)
        self.db.connection.commit()

    def tearDown(self):
        self.db.connection.close()
        os.unlink(self.path)

    def test_add_duplicate_raises_value_error(self):
        """Строки 56–58: IntegrityError → ValueError."""
        self.db.add_triangle(3, 4, 5, "Scalene (разносторонний)")
        with self.assertRaises(ValueError):
            self.db.add_triangle(3, 4, 5, "Scalene (разносторонний)")

    def test_delete_existing_returns_true(self):
        """Строки 111–119: delete_triangle, запись была."""
        self.db.add_triangle(3, 4, 5, "Scalene (разносторонний)")
        self.assertTrue(self.db.delete_triangle(3, 4, 5))
        self.assertIsNone(self.db.get_triangle(3, 4, 5))

    def test_delete_missing_returns_false(self):
        """Строки 111–119: delete_triangle, записи не было."""
        self.assertFalse(self.db.delete_triangle(9, 9, 9))


# ---------- notifier.py: 40 (TypeError) ----------

class NotifierCoverageTests(unittest.TestCase):

    def test_send_non_string_raises_type_error(self):
        """Строка 40: защита от не-строки."""
        n = EmailNotifier(recipient="a@b.c")
        with self.assertRaises(TypeError):
            n.send(123)

    def test_send_list_raises_type_error(self):
        n = EmailNotifier(recipient="a@b.c")
        with self.assertRaises(TypeError):
            n.send(["not", "a", "string"])

    def test_send_returns_false_when_no_recipient(self):
        n = EmailNotifier(recipient="")
        self.assertFalse(n.send("body"))
        self.assertEqual(n.get_sent_messages(), [])
        self.assertEqual(n.get_sent_log(), [])


# ---------- triangles_controller.py: 49 (NaN ветка) ----------

class ControllerCoverageTests(unittest.TestCase):

    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.db = TriangleDatabase(self.path)
        self.db.connection.executescript(SCHEMA_SQL)
        self.db.connection.commit()

    def tearDown(self):
        self.db.connection.close()
        os.unlink(self.path)

    def test_nan_input_stored_as_error(self):
        """Строка 49: ветка tri_type == '' (NaN)."""
        from unittest import mock
        from notifier import Notifier

        notifier = mock.Mock(spec=Notifier)
        notifier.send.return_value = True

        with mock.patch("builtins.input", side_effect=["nan 1 1"]):
            ui = ConsoleUserInterface(output_func=lambda _: None)
            ctrl = TriangleController(ui, self.db, notifier)
            result = ctrl.process_user_request()

        self.assertEqual(result["source"], "computed")
        self.assertIsNone(result["triangle_type"])
        self.assertEqual(result["error_message"], "Некорректный ввод (NaN)")


# ---------- user_interface.py: 53-54, 57-59, 67-68, 75 ----------

class UICoverageTests(unittest.TestCase):

    def test_wrong_count_of_values_then_accepts(self):
        """Строки 53–54: повтор при неверном количестве чисел."""
        values = iter(["1 2", "1 2 3"])
        captured = []
        ui = ConsoleUserInterface(
            input_func=lambda _: next(values),
            output_func=captured.append,
        )
        sides = ui.get_triangle_sides()
        self.assertEqual(sides, (1.0, 2.0, 3.0))
        self.assertTrue(any("три числа" in m for m in captured))

    def test_non_numeric_then_accepts(self):
        """Строки 57–59: повтор при нечисловом значении."""
        values = iter(["a b c", "1 2 3"])
        captured = []
        ui = ConsoleUserInterface(
            input_func=lambda _: next(values),
            output_func=captured.append,
        )
        sides = ui.get_triangle_sides()
        self.assertEqual(sides, (1.0, 2.0, 3.0))
        self.assertTrue(any("не является числом" in m for m in captured))

    def test_show_triangle_info_none(self):
        """Строки 67–68: ветка «запись не найдена»."""
        captured = []
        ui = ConsoleUserInterface(
            input_func=lambda _: "",
            output_func=captured.append,
        )
        ui.show_triangle_info(None)
        self.assertEqual(captured, ["Запись не найдена."])

    def test_show_triangle_info_with_error_message(self):
        """Строка 75: ветка с error_message."""
        captured = []
        ui = ConsoleUserInterface(
            input_func=lambda _: "",
            output_func=captured.append,
        )
        ui.show_triangle_info({
            "side_a": 1, "side_b": 2, "side_c": 10,
            "triangle_type": None,
            "error_message": "Не треугольник",
        })
        self.assertTrue(any("Ошибка" in m and "Не треугольник" in m for m in captured))
        self.assertFalse(any("Тип:" in m for m in captured))


if __name__ == "__main__":
    unittest.main()