"""Formatting module."""
from __future__ import annotations

import locale
import math
from typing import Any
from typing import Callable

import irpf_investidor.responses as res


def set_pt_br_locale() -> res.ResponseFailure | res.ResponseSuccess:
    """Sets pt_BR locale."""
    # one gets available locale from shell `locale -a`
    supported_locales = ["pt_BR.utf8", "pt_BR.UTF-8"]
    for loc in supported_locales:
        try:
            locale.setlocale(locale.LC_ALL, loc)
            return res.ResponseSuccess()
        except locale.Error:
            pass
    return res.ResponseFailure(
        res.ResponseTypes.SYSTEM_ERROR,
        "locale pt_BR não encontrado, confira a documentação para mais informações.",
    )


def get_currency_format() -> Callable[[Any], str]:
    """Return currency function.

    Returns:
        Callable[[Any], str]: function from current locale.
    """
    return locale.currency


def fmt_money(amount: float, ndigits: int = 2) -> str:
    """Return padded and rounded value."""
    if math.isnan(amount):
        return "N/A"
    rounded = round(amount, ndigits)
    result = str(rounded).replace(".", ",")
    rounded_digits = result.split(",")[1]
    missing_digits = ndigits - len(rounded_digits)
    padded_result = result + "0" * missing_digits
    return padded_result
