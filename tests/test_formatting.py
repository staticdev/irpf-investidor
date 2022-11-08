"""Test cases for formatting module."""
import locale

from pytest_mock import MockerFixture

from irpf_investidor import formatting


def test_set_pt_br_locale_success(mocker: MockerFixture) -> None:
    """Return success."""
    mocker.patch("locale.setlocale")
    assert bool(formatting.set_pt_br_locale()) is True


def test_set_pt_br_locale_error(mocker: MockerFixture) -> None:
    """Return pt_BR locale."""
    mocker.patch("locale.setlocale", side_effect=locale.Error())
    response = formatting.set_pt_br_locale()

    assert bool(response) is False
    assert (
        response.value["message"]
        == "locale pt_BR não encontrado, confira a documentação para mais informações."
    )


def test_get_currency_format(mocker: MockerFixture) -> None:
    """Give no error."""
    formatting.get_currency_format()


def test_fmt_money_no_padding() -> None:
    """Return rounded value."""
    num = 1581.12357
    digits = 3
    expected = "1581,124"

    assert formatting.fmt_money(num, digits) == expected


def test_fmt_money_with_padding() -> None:
    """Return rounded and padded value."""
    num = 1581.1
    digits = 3
    expected = "1581,100"

    assert formatting.fmt_money(num, digits) == expected


def test_fmt_money_is_nan() -> None:
    """Return N/A."""
    num = float("nan")
    digits = 2
    expected = "N/A"

    assert formatting.fmt_money(num, digits) == expected
