# modified version of
# https://brownan.github.io/lazy-allocation/Lazy%20Portfolio%20Allocation%20Algorithm.html

from fractions import Fraction
from typing import Dict, List

from gnucash_asset_allocation.gnucash import Asset


class LazyAsset:
    def __init__(self, asset: Asset) -> None:
        self.ticker: str = asset.ticker

        self.a: Fraction = asset.amount * asset.currency_conversion
        self.d: Fraction = asset.desired_allocation
        self.t: Fraction = Fraction(0)
        self.f: Fraction = Fraction(0)
        self.delta: Fraction = Fraction(0)
        self.i: int = -1


def lazy_alloc(assets: List[Asset], C: Fraction) -> Dict[str, Fraction]:
    l_assets = [LazyAsset(asset) for asset in assets]

    T = sum(Fraction(asset.a) for asset in l_assets) + Fraction(C)
    for asset_index, asset in enumerate(l_assets):
        asset.t = T * Fraction(asset.d) or Fraction("0.001")
        asset.f = Fraction(asset.a) / asset.t
        asset.i = asset_index
    C = Fraction(C)

    l_assets.sort(key=lambda asset: asset.f)
    if C < 0:
        l_assets.reverse()

    step = 0
    r = Fraction(0)
    prev_TC = Fraction(0)

    while True:
        this_f = l_assets[step].f
        r += l_assets[step].t

        if step + 1 == len(l_assets):
            break

        next_f = l_assets[step + 1].f
        TC = prev_TC + r * (next_f - this_f)

        if abs(TC) >= abs(C):
            break

        step += 1
        prev_TC = TC

    f_f = this_f + (C - prev_TC) / r

    for asset_index, asset in enumerate(l_assets):
        if asset_index <= step:
            asset.delta = asset.t * (f_f - asset.f)
        else:
            asset.delta = Fraction(0)

    return {asset.ticker: asset.delta for asset in l_assets}
