"""Test cases for the __main__ module."""
import click.testing
import pytest
from pytest_mock import MockerFixture

from irpf_investidor import __main__
from irpf_investidor import responses as res


@pytest.fixture
def runner() -> click.testing.CliRunner:
    """Fixture for invoking command-line interfaces."""
    return click.testing.CliRunner()


@pytest.fixture
def mock_cei_get_xls_filename(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking report_reader.get_xls_filename."""
    return mocker.patch("irpf_investidor.report_reader.get_xls_filename")


@pytest.fixture
def mock_cei_validate_header(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking report_reader.validate."""
    mock = mocker.patch("irpf_investidor.report_reader.validate_header")
    mock.return_value = 2019, "ABC"
    return mock


@pytest.fixture
def mock_cei_read_xls(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking report_reader.read_xls."""
    return mocker.patch("irpf_investidor.report_reader.read_xls")


@pytest.fixture
def mock_cei_clean_table_cols(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking report_reader.clean_table_cols."""
    return mocker.patch("irpf_investidor.report_reader.clean_table_cols")


@pytest.fixture
def mock_cei_group_trades(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking report_reader.group_trades."""
    return mocker.patch("irpf_investidor.report_reader.group_trades")


@pytest.fixture
def mock_select_trades(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking prompt.select_trades."""
    return mocker.patch("irpf_investidor.prompt.select_trades")


@pytest.fixture
def mock_cei_get_trades(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking report_reader.get_trades."""
    return mocker.patch("irpf_investidor.report_reader.get_trades")


@pytest.fixture
def mock_cei_calculate_taxes(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking report_reader.calculate_taxes."""
    return mocker.patch("irpf_investidor.report_reader.calculate_taxes")


@pytest.fixture
def mock_cei_output_taxes(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking report_reader.output_taxes."""
    return mocker.patch("irpf_investidor.report_reader.output_taxes")


@pytest.fixture
def mock_cei_goods_and_rights(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking report_reader.goods_and_rights."""
    return mocker.patch("irpf_investidor.report_reader.goods_and_rights")


@pytest.fixture
def mock_cei_output_goods_and_rights(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking report_reader.output_goods_and_rights."""
    return mocker.patch("irpf_investidor.report_reader.output_goods_and_rights")


def test_main_succeeds(
    mocker: MockerFixture,
    runner: click.testing.CliRunner,
    mock_cei_get_xls_filename: MockerFixture,
    mock_cei_validate_header: MockerFixture,
    mock_cei_read_xls: MockerFixture,
    mock_cei_clean_table_cols: MockerFixture,
    mock_cei_group_trades: MockerFixture,
    mock_select_trades: MockerFixture,
    mock_cei_get_trades: MockerFixture,
    mock_cei_calculate_taxes: MockerFixture,
    mock_cei_output_taxes: MockerFixture,
    mock_cei_goods_and_rights: MockerFixture,
    mock_cei_output_goods_and_rights: MockerFixture,
) -> None:
    """Exit with a status code of zero."""
    mocker.patch(
        "irpf_investidor.formatting.set_pt_br_locale",
        return_value=res.ResponseSuccess(),
    )
    result = runner.invoke(__main__.main)
    assert result.output.startswith("Nome do arquivo: ")
    mock_cei_calculate_taxes.assert_called_once()
    mock_cei_output_taxes.assert_called_once()
    mock_cei_goods_and_rights.assert_called_once()
    mock_cei_output_goods_and_rights.assert_called_once()
    assert result.exit_code == 0


def test_main_locale_fail(
    mocker: MockerFixture,
    runner: click.testing.CliRunner,
    mock_cei_get_xls_filename: MockerFixture,
    mock_cei_validate_header: MockerFixture,
    mock_cei_read_xls: MockerFixture,
    mock_cei_clean_table_cols: MockerFixture,
    mock_cei_group_trades: MockerFixture,
    mock_select_trades: MockerFixture,
    mock_cei_get_trades: MockerFixture,
    mock_cei_calculate_taxes: MockerFixture,
    mock_cei_output_taxes: MockerFixture,
    mock_cei_goods_and_rights: MockerFixture,
    mock_cei_output_goods_and_rights: MockerFixture,
) -> None:
    """Exit with `SystemExit` when locale not found."""
    locale_fail = res.ResponseFailure(
        res.ResponseTypes.SYSTEM_ERROR, "locale xyz não encontrado."
    )
    mocker.patch(
        "irpf_investidor.formatting.set_pt_br_locale", return_value=locale_fail
    )
    result = runner.invoke(__main__.main)

    assert result.output.startswith("Erro: locale xyz não encontrado.")
    assert type(result.exception) == SystemExit
