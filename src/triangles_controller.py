from typing import Optional

from database import TriangleDatabase
from triangles import solve
from user_interface import UserInterface


class TriangleController:
    """Бизнес-логика сквозного сценария (см. исходный docstring)."""

    def __init__(
        self,
        ui: UserInterface,
        db: TriangleDatabase,
        notifier,
    ):
        self.ui = ui
        self.db = db
        self.notifier = notifier

    def process_user_request(self) -> dict:
        side_a, side_b, side_c = self.ui.get_triangle_sides()

        record = self.db.get_triangle(side_a, side_b, side_c)
        if record is not None:
            result = {
                "side_a": record["side_a"],
                "side_b": record["side_b"],
                "side_c": record["side_c"],
                "triangle_type": record["triangle_type"],
                "error_message": record["error_message"],
                "coords": None,
                "source": "db",
            }
            self.ui.show_triangle_info(record)
        else:
            result = self._compute_and_store(side_a, side_b, side_c)
            self.ui.show_message(
                f"Результат вычислен: {result['triangle_type'] or result['error_message']}"
            )

        self.notifier.send(self._format_message(result))
        return result

    def _compute_and_store(self, side_a, side_b, side_c) -> dict:
        tri_type, coords = solve(str(side_a), str(side_b), str(side_c))

        if tri_type == "":
            triangle_type, error_message = None, "Некорректный ввод (NaN)"
        elif tri_type == "Not a triangle":
            triangle_type, error_message = None, "Не треугольник"
        else:
            triangle_type, error_message = tri_type, None

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
        if result.get("error_message"):
            return (
                f"Стороны ({result['side_a']}, {result['side_b']}, "
                f"{result['side_c']}): {result['error_message']}"
            )
        return (
            f"Стороны ({result['side_a']}, {result['side_b']}, "
            f"{result['side_c']}): {result['triangle_type']}"
        )