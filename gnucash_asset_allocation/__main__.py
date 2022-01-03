import functools
import logging
import sys
from fractions import Fraction
from typing import Dict, List

from tabulate import tabulate

from gnucash_asset_allocation.config import Config, InvalidConfigException
from gnucash_asset_allocation.gnucash import Asset, Book, BookError
from gnucash_asset_allocation.lazy_asset_allocation import lazy_alloc


def _print_usage():
    print(f"Usage: {sys.argv[0]} <Contribution Amount>", file=sys.stderr)


def _print_table(
    assets: Dict[str, Asset],
    amount_to_contribute: Dict[str, Fraction],
    portfolio_value: Fraction,
    contribution_amount: Fraction,
    base_currency: str,
):
    new_portfolio_value: Fraction = portfolio_value + contribution_amount
    table: List[List[str]] = []
    amount_used: Fraction = Fraction(0)

    for ticker in amount_to_contribute:
        initial_allocation: float = float(assets[ticker].amount / portfolio_value) * 100
        shares_to_buy: int = round(amount_to_contribute[ticker] / assets[ticker].price)
        amount_increase: Fraction = (
            shares_to_buy * assets[ticker].price * assets[ticker].currency_conversion
        )
        amount_to_buy: float = float(
            amount_increase / assets[ticker].currency_conversion
        )
        final_allocation: float = (
            float((assets[ticker].amount + amount_increase) / new_portfolio_value) * 100
        )
        amount_used += amount_increase

        table.append(
            [
                ticker,
                f"{float(assets[ticker].price):.2f} ({assets[ticker].currency})",
                f"{initial_allocation:.2f}%",
                f"{float(assets[ticker].desired_allocation):.2f}%",
                f"{final_allocation:.2f}%",
                f"{amount_to_buy:.2f} ({assets[ticker].currency})",
                f"{shares_to_buy}",
            ]
        )

    print(
        tabulate(
            table,
            headers=[
                "Asset Name",
                "Share Price",
                "Initial Allocation",
                "Target Allocation",
                "Final Allocation",
                "Amount to Buy(+) or Sell(-)",
                "Shares to Buy(+) or Sell(-)",
            ],
            tablefmt="presto",
        )
    )

    print()
    if amount_used >= 0:
        print(
            f"Cash left over: {float(contribution_amount - amount_used):.2f}",
            end=" ",
        )
    else:
        print(f"\nCash Received: {-float(amount_used):.2f}", end=" ")
    print(base_currency)


def main():
    if len(sys.argv) != 2:
        _print_usage()
        sys.exit(1)

    try:
        contribution_amount: Fraction = Fraction(round(float(sys.argv[1]), 2))
    except ValueError:
        _print_usage()
        sys.exit(1)

    try:
        config: Config = Config()
    except InvalidConfigException as e:
        logging.error(str(e))
        sys.exit(1)

    book: Book = Book(config.file)

    try:
        assets: Dict[str, Asset] = book.get_assets_in_account(config.account)
    except BookError as e:
        logging.error(str(e))
        sys.exit(1)

    portfolio_value: Fraction = functools.reduce(
        lambda a, b: a + b.amount * b.currency_conversion,
        assets.values(),
        Fraction(0),
    )

    for ticker in assets:
        assets[ticker].desired_allocation = Fraction(config.allocation[ticker])

    amount_to_contribute = lazy_alloc(
        [assets[ticker] for ticker in assets], Fraction(contribution_amount)
    )

    _print_table(
        assets,
        amount_to_contribute,
        portfolio_value,
        contribution_amount,
        book.base_currency,
    )


if __name__ == "__main__":
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.WARNING)
    main()
