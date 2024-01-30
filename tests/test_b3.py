"""Test cases for the B3 module."""

import datetime

import pytest

from irpf_investidor import b3


def test_get_asset_info_etf() -> None:
    """Return ETF."""
    asset_info = b3.get_asset_info("BOVA11")
    assert asset_info.category == "ETF"
    assert asset_info.cnpj == "10.406.511/0001-61"


def test_get_asset_info_fii() -> None:
    """Return FII."""
    asset_info = b3.get_asset_info("DOVL11B")
    assert asset_info.category == "FII"
    assert asset_info.cnpj == "10.522.648/0001-81"


def test_get_asset_info_stock() -> None:
    """Return STOCKS."""
    asset_info = b3.get_asset_info("PETR4")
    assert asset_info.category == "STOCKS"
    assert asset_info.cnpj == "33.000.167/0001-01"


def test_get_asset_info_stock_fractionary() -> None:
    """Return STOCKS."""
    asset_info = b3.get_asset_info("PETR4F")
    assert asset_info.category == "STOCKS"
    assert asset_info.cnpj == "33.000.167/0001-01"


def test_get_asset_info_not_found() -> None:
    """Return NOT_FOUND."""
    asset_info = b3.get_asset_info("OMG3M3")
    assert asset_info.category == "NOT_FOUND"


def test_get_liquidacao_rates_error() -> None:
    """Raise `SystemExit` when date is not found."""
    series = [datetime.datetime(1930, 2, 20)]
    with pytest.raises(SystemExit):
        assert b3.get_liquidacao_rates(series)


def test_get_liquidacao_rates_success() -> None:
    """Return date rates."""
    series = [
        datetime.datetime(2019, 2, 20),
        datetime.datetime(2021, 12, 31),
    ]
    expected = [0.000275, 0.00025]
    result = b3.get_liquidacao_rates(series)
    assert result == expected


def test_get_emolumentos_rates_error() -> None:
    """Raise `SystemExit` when date is not found."""
    series = [datetime.datetime(1930, 2, 20)]
    with pytest.raises(SystemExit):
        assert b3.get_emolumentos_rates(series, [])


def test_get_emolumentos_rates_sucess_no_auction() -> None:
    """Return date rates."""
    series = [
        datetime.datetime(2019, 2, 20),
        datetime.datetime(2019, 3, 6),
        datetime.datetime(2019, 5, 14),
        datetime.datetime(2019, 12, 31),
    ]
    expected = [0.00004032, 0.00004157, 0.00004408, 0.00003802]
    result = b3.get_emolumentos_rates(series, [])
    assert result == expected


def test_get_emolumentos_rates_sucess_with_auction() -> None:
    """Return date rates and auction rates."""
    series = [
        datetime.datetime(2019, 2, 20),
        datetime.datetime(2019, 3, 6),
        datetime.datetime(2019, 5, 14),
        datetime.datetime(2019, 12, 31),
    ]
    expected = [0.00004032, 0.00007, 0.00007, 0.00003802]
    result = b3.get_emolumentos_rates(series, [1, 2])
    assert result == expected


def test_get_cnpj_institution_found() -> None:
    """Return a known CNPJ."""
    institution = "90 - EASYNVEST - TITULO CV S.A."
    result = b3.get_cnpj_institution(institution)
    assert result == "62.169.875/0001-79"


def test_get_cnpj_institution_not_found() -> None:
    """Return a known CNPJ."""
    institution = "9999 - UNKNOWN S.A."
    result = b3.get_cnpj_institution(institution)
    assert result == "não encontrado"
