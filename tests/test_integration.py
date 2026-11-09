import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")),
)

from triangles_controller import TriangleController
from database import TriangleDatabase
from notifier import Notifier, EmailNotifier
from user_interface import ConsoleUserInterface, UserInterface


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


class IntegrationTestBase(unittest.TestCase):
    """Реальная SQLite во временном файле — изоляция на каждый тест."""

    def setUp(self):
        fd, self._db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.db = TriangleDatabase(self._db_path)
        self.db.connection.executescript(SCHEMA_SQL)
        self.db.connection.commit()

    def tearDown(self):
        self.db.connection.close()
        os.unlink(self._db_path)


# ---------- интеграционные тесты ----------

class TestIntegrationEndToEnd(IntegrationTestBase):
    """
    Реальные UI + БД + Controller. Mock — только на границах:
    builtins.input (пользовательский ввод) и Notifier (внешний сервер).
    """

    @mock.patch("builtins.input", side_effect=["3 4 5"])
    def test_new_record_computed_stored_and_sent(self, mock_input):
        notifier = mock.Mock(spec=Notifier)
        notifier.send.return_value = True

        ui = ConsoleUserInterface(output_func=lambda _: None)
        ctrl = TriangleController(ui, self.db, notifier)
        result = ctrl.process_user_request()

        self.assertEqual(result["source"], "computed")
        self.assertEqual(result["triangle_type"], "Scalene (разносторонний)")
        self.assertIsNotNone(result["coords"])

        record = self.db.get_triangle(3, 4, 5)
        self.assertIsNotNone(record)
        self.assertEqual(record["triangle_type"], "Scalene (разносторонний)")

        notifier.send.assert_called_once()
        message = notifier.send.call_args[0][0]
        self.assertIn("Scalene", message)
        mock_input.assert_called()

    @mock.patch("builtins.input", side_effect=["3 4 5"])
    def test_existing_record_used_without_recomputation(self, mock_input):
        self.db.add_triangle(3, 4, 5, "ОСОБЫЙ ТИП ИЗ БД")

        notifier = mock.Mock(spec=Notifier)
        notifier.send.return_value = True

        ui = ConsoleUserInterface(output_func=lambda _: None)
        ctrl = TriangleController(ui, self.db, notifier)
        result = ctrl.process_user_request()

        self.assertEqual(result["source"], "db")
        self.assertEqual(result["triangle_type"], "ОСОБЫЙ ТИП ИЗ БД")
        self.assertIsNone(result["coords"])
        self.assertEqual(len(self.db.get_all_triangles()), 1)
        notifier.send.assert_called_once()

    @mock.patch("builtins.input", side_effect=["3 4 5", "3 4 5"])
    def test_repeated_calls_use_cache(self, mock_input):
        notifier = mock.Mock(spec=Notifier)
        notifier.send.return_value = True

        ui = ConsoleUserInterface(output_func=lambda _: None)
        ctrl = TriangleController(ui, self.db, notifier)

        r1 = ctrl.process_user_request()
        r2 = ctrl.process_user_request()

        self.assertEqual(r1["source"], "computed")
        self.assertEqual(r2["source"], "db")
        self.assertEqual(len(self.db.get_all_triangles()), 1)
        self.assertEqual(notifier.send.call_count, 2)

    @mock.patch("builtins.input", side_effect=["1 2 10"])
    def test_invalid_triangle_stored_as_error_and_sent(self, mock_input):
        notifier = mock.Mock(spec=Notifier)
        notifier.send.return_value = True

        ui = ConsoleUserInterface(output_func=lambda _: None)
        ctrl = TriangleController(ui, self.db, notifier)
        result = ctrl.process_user_request()

        self.assertEqual(result["source"], "computed")
        self.assertIsNone(result["triangle_type"])
        self.assertEqual(result["error_message"], "Не треугольник")

        record = self.db.get_triangle(1, 2, 10)
        self.assertIsNotNone(record)
        self.assertIsNone(record["triangle_type"])
        self.assertEqual(record["error_message"], "Не треугольник")

        notifier.send.assert_called_once()
        self.assertIn("Не треугольник", notifier.send.call_args[0][0])

    @mock.patch("builtins.input", side_effect=["3 3 3", "3 4 5", "1 2 10"])
    def test_multiple_different_triangles_accumulate(self, mock_input):
        notifier = mock.Mock(spec=Notifier)
        notifier.send.return_value = True

        ui = ConsoleUserInterface(output_func=lambda _: None)
        ctrl = TriangleController(ui, self.db, notifier)

        for _ in range(3):
            ctrl.process_user_request()

        self.assertEqual(len(self.db.get_all_triangles()), 3)
        self.assertEqual(notifier.send.call_count, 3)

    @mock.patch("builtins.input", side_effect=["3 4 5"])
    def test_real_email_notifier_in_full_flow(self, mock_input):
        """Реальный EmailNotifier (не mock) — проверяем и этот путь интеграции."""
        notifier = EmailNotifier(recipient="test@example.com")
        ui = ConsoleUserInterface(output_func=lambda _: None)
        ctrl = TriangleController(ui, self.db, notifier)

        ctrl.process_user_request()

        sent = notifier.get_sent_messages()
        self.assertEqual(len(sent), 1)
        self.assertIn("Scalene", sent[0])
        log = notifier.get_sent_log()
        self.assertEqual(log[0]["to"], "test@example.com")
        self.assertIsNotNone(self.db.get_triangle(3, 4, 5))


# ---------- юнит-тесты (не дублируют Лаб.2) ----------

class TestUnitNonDuplicate(unittest.TestCase):

    def test_controller_accepts_any_notifier_implementation(self):
        """
        Полиморфизм: Controller одинаково работает с mock-реализацией
        и с реальным EmailNotifier.
        """
        class StubUI(UserInterface):
            def get_triangle_sides(self): return (3.0, 4.0, 5.0)
            def show_message(self, m): pass
            def show_triangle_info(self, i): pass

        class StubDB:
            def get_triangle(self, a, b, c): return None
            def add_triangle(self, a, b, c, t, e=None): return 1

        mock_notifier = mock.Mock(spec=Notifier)
        mock_notifier.send.return_value = True
        real_notifier = EmailNotifier(recipient="a@b.c")

        for notifier in [mock_notifier, real_notifier]:
            ctrl = TriangleController(StubUI(), StubDB(), notifier)
            result = ctrl.process_user_request()
            self.assertEqual(result["source"], "computed")

        mock_notifier.send.assert_called_once()

    def test_controller_returns_result_even_if_notifier_fails(self):
        """
        Если mock-имитация внешнего сервера возвращает False,
        Controller всё равно возвращает валидный результат, а данные сохранены.
        """
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            db = TriangleDatabase(path)
            db.connection.executescript(SCHEMA_SQL)
            db.connection.commit()

            notifier = mock.Mock(spec=Notifier)
            notifier.send.return_value = False  # имитация неудачи

            with mock.patch("builtins.input", side_effect=["3 4 5"]):
                ui = ConsoleUserInterface(output_func=lambda _: None)
                ctrl = TriangleController(ui, db, notifier)
                result = ctrl.process_user_request()

            self.assertEqual(result["source"], "computed")
            self.assertEqual(result["triangle_type"], "Scalene (разносторонний)")
            notifier.send.assert_called_once()
            self.assertIsNotNone(db.get_triangle(3, 4, 5))

            db.connection.close()
        finally:
            os.unlink(path)

    def test_data_persists_after_reconnect(self):
        """Данные из одного соединения видны после повторного открытия файла."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            db1 = TriangleDatabase(path)
            db1.connection.executescript(SCHEMA_SQL)
            db1.connection.commit()
            db1.add_triangle(3, 4, 5, "Scalene (разносторонний)")
            db1.connection.close()

            db2 = TriangleDatabase(path)
            record = db2.get_triangle(3, 4, 5)
            self.assertIsNotNone(record)
            self.assertEqual(record["triangle_type"], "Scalene (разносторонний)")
            db2.connection.close()
        finally:
            os.unlink(path)

    @mock.patch("builtins.input", side_effect=["3 4 5"])
    def test_input_called_once_and_returns_expected(self, mock_input):
        """mock.patch для input: проверяем, что реальный stdin не тронут."""
        ui = ConsoleUserInterface(output_func=lambda _: None)
        sides = ui.get_triangle_sides()
        self.assertEqual(sides, (3.0, 4.0, 5.0))
        mock_input.assert_called_once()


if __name__ == "__main__":
    unittest.main()