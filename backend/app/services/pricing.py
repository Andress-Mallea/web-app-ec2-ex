from abc import ABC, abstractmethod
from datetime import date

LONG_STAY_MIN_NIGHTS = 7
LONG_STAY_DISCOUNT = 0.10
LATE_CANCEL_DAYS = 2


class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, nights: int, price_per_night: float) -> float:
        """Calcula el precio total de la estadía."""


class StandardPricing(PricingStrategy):
    def calculate(self, nights: int, price_per_night: float) -> float:
        return round(nights * price_per_night, 2)


class LongStayDiscountPricing(PricingStrategy):
    def calculate(self, nights: int, price_per_night: float) -> float:
        return round(nights * price_per_night * (1 - LONG_STAY_DISCOUNT), 2)


def select_pricing_strategy(nights: int) -> PricingStrategy:
    if nights >= LONG_STAY_MIN_NIGHTS:
        return LongStayDiscountPricing()
    return StandardPricing()


def calculate_cancellation_total(check_in: date, today: date, price_per_night: float) -> float:
    if (check_in - today).days < LATE_CANCEL_DAYS:
        return round(price_per_night, 2)
    return 0.0