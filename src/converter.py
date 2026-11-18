class Converter:
    """Входные данные должны иметь не более одного знака после запятой."""
    @staticmethod
    def do(x: float) -> int:
        if round(x, 1) != x:
            raise ValueError(
                f"Число {x!r} имеет более одного знака после запятой"
            )

        if x >= 100.7:
            return 1000

        if x > 0:
            return int(x)

        if x == 0.0:
            raise ValueError("x не может быть равен 0.0")

        if x >= -30.5:
            return int(x) - 5

        return -2000