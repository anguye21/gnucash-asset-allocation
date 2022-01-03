import functools
from fractions import Fraction
from typing import Dict, List

import piecash

from .asset import Asset


class BookError(Exception):
    pass


class Book:
    def __init__(self, file: str) -> None:
        self.book: piecash.Book = piecash.open_book(
            file, readonly=True, open_if_lock=True
        )
        self.base_currency: str = self.book.root_account.commodity.mnemonic
        self._currency_coversions: dict[str, Fraction] = {}

    def get_assets_in_account(self, account_name: str) -> Dict[str, Asset]:
        assets: Dict[str, Asset] = {}
        account: piecash.Account = self.book.accounts.get(fullname=account_name)
        investments: List[piecash.Account] = self._get_investments_in_account(account)

        for investment in investments:
            ticker: str = investment.commodity.mnemonic
            try:
                price: piecash.Commodity = functools.reduce(
                    lambda a, b: a if a.date > b.date else b,
                    investment.commodity.prices,
                )
            except TypeError as e:
                raise BookError(f"No price information for {ticker}") from e

            num_shares: float = investment.get_balance()
            assets[ticker] = Asset(
                ticker=ticker,
                price=Fraction(price.value),
                currency=price.currency.mnemonic,
                currency_conversion=self._to_base_currency_conversion(price.currency),
                num_shares=Fraction(num_shares),
            )

        return assets

    def _get_investments_in_account(
        self,
        account: piecash.Account,
    ) -> List[piecash.Account]:
        investments = []

        for sub_account in account.children:
            if sub_account.type in ("STOCK", "MUTUAL"):
                investments.append(sub_account)
            else:
                investments += self._get_investments_in_account(sub_account)

        return investments

    def _to_base_currency_conversion(self, currency: piecash.Commodity) -> Fraction:
        if currency.mnemonic == self.base_currency:
            return Fraction(1)

        if currency.mnemonic in self._currency_coversions:
            return self._currency_coversions[currency.mnemonic]

        coversion_rate = Fraction(
            functools.reduce(
                lambda a, b: a if a.date > b.date else b,
                currency.prices,
            ).value
        )

        self._currency_coversions[currency.mnemonic] = coversion_rate

        return coversion_rate
