from fractions import Fraction

import pytest

from gnucash_asset_allocation.gnucash import Asset, Book, BookError

# TODO: create fake objects instead of reading files


def test_get_assets_in_account():
    book = Book("tests/books/sample.gnucash")
    assets = book.get_assets_in_account("Assets:Investments:Brokerage Account")

    assert assets == {
        "SPY": Asset(
            ticker="SPY",
            price=Fraction(500),
            num_shares=Fraction(5),
            currency="USD",
            currency_conversion=Fraction(1),
            desired_allocation=Fraction(0),
        ),
        "QQQ": Asset(
            ticker="QQQ",
            price=Fraction(400),
            num_shares=Fraction(7),
            currency="USD",
            currency_conversion=Fraction(1),
            desired_allocation=Fraction(0),
        ),
    }


def test_get_assets_in_account_multiple_currencies():
    book = Book("tests/books/sample-multiple-currencies.gnucash")
    assets = book.get_assets_in_account("Assets:Investments:Brokerage Account")

    assert assets == {
        "SPY": Asset(
            ticker="SPY",
            price=Fraction(500),
            num_shares=Fraction(5),
            currency="USD",
            currency_conversion=Fraction(1),
            desired_allocation=Fraction(0),
        ),
        "QQQ": Asset(
            ticker="QQQ",
            price=Fraction(400),
            num_shares=Fraction(7),
            currency="USD",
            currency_conversion=Fraction(1),
            desired_allocation=Fraction(0),
        ),
        "^STOXX": Asset(
            ticker="^STOXX",
            price=Fraction(490),
            num_shares=Fraction(2),
            currency="EUR",
            currency_conversion=Fraction(36, 25),
            desired_allocation=Fraction(0),
        ),
    }


def test_get_assets_in_account_no_prices():
    book = Book("tests/books/sample-no-prices.gnucash")

    with pytest.raises(BookError):
        book.get_assets_in_account("Assets:Investments:Brokerage Account")
