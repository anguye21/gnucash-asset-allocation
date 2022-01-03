from fractions import Fraction

import pytest

from gnucash_asset_allocation.gnucash import Asset
from gnucash_asset_allocation.lazy_asset_allocation import lazy_alloc


@pytest.mark.parametrize(
    "assets,contribution_amount,deltas",
    [
        (
            [
                Asset(
                    ticker="T1",
                    price=Fraction(1),
                    num_shares=Fraction(600),
                    currency="USD",
                    currency_conversion=Fraction(1),
                    desired_allocation=Fraction(70),
                ),
                Asset(
                    ticker="T2",
                    price=Fraction(1),
                    num_shares=Fraction(200),
                    currency="USD",
                    currency_conversion=Fraction(1),
                    desired_allocation=Fraction(30),
                ),
            ],
            Fraction(200),
            {
                "T1": Fraction(100),
                "T2": Fraction(100),
            },
        ),
        (
            [
                Asset(
                    ticker="T1",
                    price=Fraction(1),
                    num_shares=Fraction(600),
                    currency="USD",
                    currency_conversion=Fraction(1),
                    desired_allocation=Fraction(50),
                ),
                Asset(
                    ticker="T2",
                    price=Fraction(1),
                    num_shares=Fraction(600),
                    currency="USD",
                    currency_conversion=Fraction(1),
                    desired_allocation=Fraction(50),
                ),
            ],
            Fraction(-200),
            {
                "T1": Fraction(-100),
                "T2": Fraction(-100),
            },
        ),
    ],
)
def test_lazy_alloc(assets, contribution_amount, deltas):
    assert lazy_alloc(assets, contribution_amount) == deltas
