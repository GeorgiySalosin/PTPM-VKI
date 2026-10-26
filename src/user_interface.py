from abc import ABC, abstractmethod


class UserInterface(ABC):
    """
    Абстрактный интерфейс взаимодействия с пользователем.
    """

    @abstractmethod
    def get_triangle_sides(self) -> tuple[float, float, float]:
        """
        Получить от пользователя три длины сторон.

        :return: кортеж (side_a, side_b, side_c).
        :raises ValueError: если пользователь ввёл нечисловые значения.
        """
        ...

    @abstractmethod
    def show_message(self, message: str) -> None:
        """Показать пользователю сообщение."""
        ...

    @abstractmethod
    def show_triangle_info(self, info: dict) -> None:
        """Показать информацию о треугольнике (запись из БД)."""
        ...


class ConsoleUserInterface(UserInterface):
    """
    Консольная реализация интерфейса.

    Читает данные через input(), пишет через print().
    """

    def __init__(self, input_func=input, output_func=print):
        """
        :param input_func: функция ввода (по умолчанию input) — удобно подменять в тестах.
        :param output_func: функция вывода (по умолчанию print) — удобно подменять в тестах.
        """
        self._input = input_func
        self._output = output_func

    def get_triangle_sides(self) -> tuple[float, float, float]:
        """
        Запросить три стороны. Повторяет ввод, пока не введены корректные числа.
        """
        while True:
            raw = self._input("Введите три стороны треугольника через пробел: ")
            parts = raw.replace(",", " ").split()
            if len(parts) != 3:
                self._output("Нужно ровно три числа. Попробуйте ещё раз.")
                continue
            try:
                a, b, c = (float(x) for x in parts)
            except ValueError:
                self._output("Одно из значений не является числом. Попробуйте ещё раз.")
                continue
            return a, b, c

    def show_message(self, message: str) -> None:
        self._output(message)

    def show_triangle_info(self, info: dict) -> None:
        if info is None:
            self._output("Запись не найдена.")
            return
        self._output(
            f"Стороны: {info['side_a']}, {info['side_b']}, {info['side_c']}"
        )
        if info.get("triangle_type"):
            self._output(f"Тип: {info['triangle_type']}")
        if info.get("error_message"):
            self._output(f"Ошибка: {info['error_message']}")