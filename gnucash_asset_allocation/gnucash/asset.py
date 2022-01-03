from dataclasses import dataclass
from fractions import Fraction


@dataclass
class Asset:
    ticker: str
    price: Fraction
    num_shares: Fraction
    currency: str
    currency_conversion: Fraction
    desired_allocation: Fraction = Fraction(0)

    @property
    def amount(self) -> Fraction:
        return self.price * self.num_shares
