import sqlite3
from typing import Optional


class TriangleDatabase:
    """
    Класс для работы с БД SQLite проекта «Треугольник».

    Одна запись:
        (side_a, side_b, side_c) -> (triangle_type, error_message)

    Идентификация записи — по трём длинам сторон.
    """

    def __init__(self, db_path: str = "triangles.db"):
        """
        :param db_path: путь к файлу БД
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        # Удобно получать строки как dict-подобные объекты
        self.connection.row_factory = sqlite3.Row


    def add_triangle(
        self,
        side_a: float,
        side_b: float,
        side_c: float,
        triangle_type: Optional[str],
        error_message: Optional[str] = None,
    ) -> int:
        """
        Добавить запись.

        :return: id вставленной записи.
        :raises ValueError: если запись с такими сторонами уже существует.
        """
        try:
            cursor = self.connection.execute(
                """
                INSERT INTO triangles
                    (side_a, side_b, side_c, triangle_type, error_message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    float(side_a),
                    float(side_b),
                    float(side_c),
                    triangle_type,
                    error_message,
                ),
            )
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:     # constraint violation
            
            raise ValueError(
                f"Запись с такими сторонами уже существует: "
                f"({side_a}, {side_b}, {side_c})"
            ) from e



    def get_triangle(
        self,
        side_a: float,
        side_b: float,
        side_c: float,
    ) -> Optional[dict]:
        """
        Получить запись по трём сторонам.

        :return: dict с полями записи или None, если не найдено.
        """
        cursor = self.connection.execute(
            """
            SELECT id, side_a, side_b, side_c, triangle_type, error_message
            FROM triangles
            WHERE side_a = ? AND side_b = ? AND side_c = ?
            """,
            (float(side_a), float(side_b), float(side_c)),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


    def get_all_triangles(self) -> list[dict]:
        """Получить все записи (полезно для отладки и тестов)."""
        cursor = self.connection.execute(
            """
            SELECT id, side_a, side_b, side_c, triangle_type, error_message
            FROM triangles
            ORDER BY id
            """
        )
        return [dict(row) for row in cursor.fetchall()]


    def delete_triangle(
        self,
        side_a: float,
        side_b: float,
        side_c: float,
    ) -> bool:
        """
        Удалить запись по трём сторонам.

        :return: True, если запись была удалена; False, в противном случае.
        """
        cursor = self.connection.execute(
            """
            DELETE FROM triangles
            WHERE side_a = ? AND side_b = ? AND side_c = ?
            """,
            (float(side_a), float(side_b), float(side_c)),
        )
        self.connection.commit()
        return cursor.rowcount > 0
