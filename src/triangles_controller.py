from typing import Optional

from database import TriangleDatabase
from triangles import solve
from user_interface import UserInterface



class TriangleController:
    """
    Бизнес-логика сквозного сценария:

    1. Запросить у пользователя стороны треугольника.
    2. Если записи в БД нет — вычислить через solve() и сохранить.
    3. Если запись есть — взять готовый результат из БД.
    4. Отправить строку-результат во внешний сервис.
    5. Вернуть результат операции.

    Все зависимости передаются через конструктор (DI), чтобы:
      - легко подменять их в тестах;
      - не создавать жёстких связей между слоями.
    """

    def __init__(
        self,
        ui: UserInterface,
        db: TriangleDatabase
    ):
        self.ui = ui
        self.db = db

    # ---------- основной сценарий ----------

    def process_user_request(self) -> dict:
        """
        Полный сценарий: ввод → проверка БД → вычисление при необходимости
        → отправка наружу → возврат результата.

        :return: dict с полями:
            - side_a, side_b, side_c
            - triangle_type (str или None)
            - error_message (str или None)
            - coords (list или None) — координаты, если треугольник валиден
            - source ("db" или "computed")
        """
        # 1. Ввод
        side_a, side_b, side_c = self.ui.get_triangle_sides()

        # 2. Проверка БД
        record = self.db.get_triangle(side_a, side_b, side_c)
        if record is not None:
            # 2а. Есть запись — берём из БД
            result = {
                "side_a": record["side_a"],
                "side_b": record["side_b"],
                "side_c": record["side_c"],
                "triangle_type": record["triangle_type"],
                "error_message": record["error_message"],
                "coords": None,  # в БД координаты не хранятся
                "source": "db",
            }
            self.ui.show_triangle_info(record)
        else:
            # 2б. Нет записи — вычисляем и сохраняем
            result = self._compute_and_store(side_a, side_b, side_c)
            self.ui.show_message(
                f"Результат вычислен: {result['triangle_type'] or result['error_message']}"
            )

        # 3. Отправка наружу
        self.notifier.send(self._format_message(result))

        # 4. Возврат
        return result

    # ---------- внутренние методы ----------

    def _compute_and_store(
        self,
        side_a: float,
        side_b: float,
        side_c: float,
    ) -> dict:
        """
        Вычислить тип треугольника через solve() и сохранить в БД.

        :return: dict в том же формате, что и process_user_request.
        """
        tri_type, coords = solve(str(side_a), str(side_b), str(side_c))

        # Приводим результат solve() к формату записи БД
        if tri_type == "":
            # NaN — фиксируем как ошибку ввода
            triangle_type = None
            error_message = "Некорректный ввод (NaN)"
        elif tri_type == "Not a triangle":
            triangle_type = None
            error_message = "Не треугольник"
        else:
            triangle_type = tri_type
            error_message = None

        new_id = self.db.add_triangle(
            side_a, side_b, side_c, triangle_type, error_message
        )

        return {
            "id": new_id,
            "side_a": float(side_a),
            "side_b": float(side_b),
            "side_c": float(side_c),
            "triangle_type": triangle_type,
            "error_message": error_message,
            "coords": coords,
            "source": "computed",
        }

    @staticmethod
    def _format_message(result: dict) -> str:
        """Сформировать строку-результат для отправки наружу."""
        if result.get("error_message"):
            return (
                f"Стороны ({result['side_a']}, {result['side_b']}, "
                f"{result['side_c']}): {result['error_message']}"
            )
        return (
            f"Стороны ({result['side_a']}, {result['side_b']}, "
            f"{result['side_c']}): {result['triangle_type']}"
        )