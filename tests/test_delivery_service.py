import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")),
)

from delivery_service import calculate_delivery_cost

ERROR = (-1, "0000-00-00")


class TestDeliveryValidation(unittest.TestCase):
    """Проверка границ: вес, дистанция, тип посылки."""

    def test_weight_below_minimum_returns_error(self):
        self.assertEqual(
            calculate_delivery_cost(0.09, 1, "обычный"),
            ERROR,
        )

    def test_weight_above_maximum_returns_error(self):
        self.assertEqual(
            calculate_delivery_cost(50.1, 1, "обычный"),
            ERROR,
        )

    def test_distance_below_minimum_returns_error(self):
        self.assertEqual(
            calculate_delivery_cost(1, 0, "обычный"),
            ERROR,
        )

    def test_distance_above_maximum_returns_error(self):
        self.assertEqual(
            calculate_delivery_cost(1, 5001, "обычный"),
            ERROR,
        )

    def test_invalid_package_type_returns_error(self):
        self.assertEqual(
            calculate_delivery_cost(1, 1, "секретный"),
            ERROR,
        )

    def test_minimum_valid_weight_and_distance_returns_base_cost(self):
        cost, date = calculate_delivery_cost(0.1, 1, "обычный")
        self.assertEqual(cost, 205)
        self.assertEqual(date, "2026-09-04")


class TestDeliveryWeightCoefficients(unittest.TestCase):
    """Весовые коэффициенты: 1.0 / 1.2 / 1.5."""

    def test_weight_exactly_five_has_no_medium_coefficient(self):
        # граница: 5.0 не попадает в диапазон (5.0 < weight < 20.0)
        cost, _ = calculate_delivery_cost(5, 100, "обычный")
        self.assertEqual(cost, 700)

    def test_medium_weight_adds_twenty_percent(self):
        # 200 + 100*5 = 700; 10 кг → *1.2 = 840
        cost, date = calculate_delivery_cost(10, 100, "обычный")
        self.assertEqual(cost, 840)
        self.assertEqual(date, "2026-09-04")

    def test_weight_exactly_twenty_uses_heavy_coefficient(self):
        # граница: 20.0 → *1.5
        cost, _ = calculate_delivery_cost(20, 100, "обычный")
        self.assertEqual(cost, 1050)

    def test_heavy_weight_adds_fifty_percent(self):
        # 700 * 1.5 = 1050
        cost, _ = calculate_delivery_cost(30, 100, "обычный")
        self.assertEqual(cost, 1050)


class TestDeliveryTypeSurcharges(unittest.TestCase):
    """Надбавки за тип посылки."""

    def test_fragile_package_adds_surcharge(self):
        # 200 + 10*5 = 250; + 300 = 550
        cost, _ = calculate_delivery_cost(3, 10, "хрупкий")
        self.assertEqual(cost, 550)

    def test_dangerous_package_adds_surcharge(self):
        # 200 + 10*5 = 250; + 1000 = 1250
        cost, _ = calculate_delivery_cost(3, 10, "опасный")
        self.assertEqual(cost, 1250)

    def test_common_package_has_no_surcharge(self):
        cost, _ = calculate_delivery_cost(3, 10, "обычный")
        self.assertEqual(cost, 250)


class TestDeliveryExpress(unittest.TestCase):
    """Экспресс-доставка: дороже и быстрее."""

    def test_express_delivery_increases_cost_and_reduces_days(self):
        # базовый расчёт: 200 + 1000*5 = 5200; express → *1.5 = 7800
        cost, date = calculate_delivery_cost(3, 1000, "обычный", is_express=True)
        self.assertEqual(cost, 7800)
        # 1000//500 = 2 дня → express → 2//2 = 1, но не меньше 1 → 1
        self.assertEqual(date, "2026-09-04")

    def test_express_delivery_keeps_at_least_one_day(self):
        # 100//500 = 0 → max(1, 0) = 1; express → 1//2 = 0 → max(1, 0) = 1
        cost, date = calculate_delivery_cost(3, 100, "обычный", is_express=True)
        self.assertEqual(cost, 1050)
        self.assertEqual(date, "2026-09-04")

    def test_express_cost_is_truncated_to_int(self):
        # 205 * 1.5 = 307.5 → int(307.5) = 307
        cost, _ = calculate_delivery_cost(0.1, 1, "обычный", is_express=True)
        self.assertEqual(cost, 307)


class TestDeliveryDates(unittest.TestCase):
    """Расчёт даты доставки: distance // 500 и максимум 1 день."""

    def test_minimum_distance_takes_one_day(self):
        _, date = calculate_delivery_cost(3, 1, "обычный")
        self.assertEqual(date, "2026-09-04")

    def test_short_distance_takes_one_day(self):
        _, date = calculate_delivery_cost(3, 499, "обычный")
        self.assertEqual(date, "2026-09-04")

    def test_boundary_distance_500_gives_one_day(self):
        # 500 // 500 = 1
        _, date = calculate_delivery_cost(3, 500, "обычный")
        self.assertEqual(date, "2026-09-04")

    def test_distance_1000_gives_two_days(self):
        _, date = calculate_delivery_cost(3, 1000, "обычный")
        self.assertEqual(date, "2026-09-05")

    def test_long_distance_splits_into_three_days(self):
        # 1500 // 500 = 3 дня
        cost, date = calculate_delivery_cost(3, 1500, "обычный")
        self.assertEqual(cost, 7700)
        self.assertEqual(date, "2026-09-06")


class TestDeliveryCombined(unittest.TestCase):
    """Комбинации условий и максимумы."""

    def test_combined_fragile_heavy_and_express(self):
        # базовый: 200 + 1000*5 = 5200
        # heavy (20 кг): *1.5 = 7800
        # fragile: +300 = 8100
        # express: *1.5 = 12150
        cost, date = calculate_delivery_cost(20, 1000, "хрупкий", is_express=True)
        self.assertEqual(cost, 12150)
        # 1000//500 = 2 → express → 2//2 = 1
        self.assertEqual(date, "2026-09-04")

    def test_maximum_valid_weight_and_distance(self):
        # базовый: 200 + 5000*5 = 25200
        # heavy (50 кг): *1.5 = 37800
        # опасный: +1000 = 38800
        cost, date = calculate_delivery_cost(50, 5000, "опасный")
        self.assertEqual(cost, 38800)
        # 5000 // 500 = 10 → 2026-09-03 + 10 = 2026-09-13
        self.assertEqual(date, "2026-09-13")


if __name__ == "__main__":
    unittest.main()