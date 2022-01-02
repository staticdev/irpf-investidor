"""Test cases for the report reader module."""
import datetime
import os

import pandas as pd
import pytest
from pytest_mock import MockerFixture

import irpf_investidor.report_reader as report_reader


B3_REPORT_NAME = "InfoCEI.xls"


def test_date_parse() -> None:
    """Return datetime."""
    expected = datetime.datetime(day=1, month=2, year=2019)
    assert report_reader.date_parse(" 01/02/19 ") == expected


@pytest.fixture
def mock_pandas_read_excel(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking pandas.read_excel."""
    mock = mocker.patch("pandas.read_excel")
    header = pd.DataFrame(
        {
            "Período de": [
                "01/01/2019 a 31/12/2019",
                float("nan"),
                float("nan"),
                float("nan"),
                "INSTITUTION",
            ]
        }
    )
    mock.return_value = header
    return mock


def test_read_xls(mock_pandas_read_excel: MockerFixture) -> None:
    """Call read_excel."""
    report_reader.read_xls("my.xls")
    mock_pandas_read_excel.assert_called_once()


def test_round_down_money_more_than_half() -> None:
    """Return rounded down two decimals."""
    assert report_reader.round_down_money(5.999) == 5.99


def test_round_down_money_on_half() -> None:
    """Return rounded down two decimals second case."""
    assert report_reader.round_down_money(5.555) == 5.55


def test_round_down_money_one_digit() -> None:
    """Return rounded down two decimals third case."""
    assert report_reader.round_down_money(8.5) == 8.50


@pytest.fixture
def cwd(fs: MockerFixture, monkeypatch: MockerFixture) -> None:
    """Fixture for pyfakefs fs."""
    fs.cwd = "/path"
    monkeypatch.setenv("HOME", "/home")


def test_get_xls_filename_not_found(fs: MockerFixture, cwd: MockerFixture) -> None:
    """Raise `SystemExit` when file is not found."""
    with pytest.raises(SystemExit):
        assert report_reader.get_xls_filename()


def test_get_xls_filename_current_folder(fs: MockerFixture, cwd: MockerFixture) -> None:
    """Return filename found in current folder."""
    fs.create_file(f"/path/{B3_REPORT_NAME}")
    assert report_reader.get_xls_filename() == B3_REPORT_NAME


def test_get_xls_filename_download_folder(
    mocker: MockerFixture, fs: MockerFixture, cwd: MockerFixture
) -> None:
    """Return filename found in downloads folder."""
    mocker.patch("os.path.expanduser", return_value="/home")
    path = os.path.join("/home", "Downloads", B3_REPORT_NAME)
    fs.create_file(path)
    assert report_reader.get_xls_filename() == path


def test_validate_period_success() -> None:
    """Return reference year."""
    first_date = "01/01/2019"
    second_date = "31/12/2020"

    assert report_reader.validate_period(first_date, second_date) == 2020


def test_validate_period_wrong_start_finish() -> None:
    """Raise `SystemExit` from wrong start date."""
    first_date = "01/01/2018"
    second_date = "31/12/2020"

    with pytest.raises(SystemExit) as ex:
        report_reader.validate_period(first_date, second_date)
    assert str(ex.value) == (
        f"Erro: o período de {first_date} a {second_date} não é válido, favor "
        "verificar instruções na documentação."
    )


def test_validate_header_empty_file(fs: MockerFixture, cwd: MockerFixture) -> None:
    """Raise `SystemExit` from empty file."""
    path = os.path.join("path", "Inforeport_reader.xls")
    fs.create_file(path)
    with pytest.raises(SystemExit):
        report_reader.validate_header(path)


@pytest.fixture
def mock_validate_period(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking irpf_investidor.report_reader.validate_period."""
    mock = mocker.patch("irpf_investidor.report_reader.validate_period")
    mock.return_value = 2019
    return mock


def test_validate_header(
    mock_pandas_read_excel: MockerFixture, mock_validate_period: MockerFixture
) -> None:
    """Return year and institution."""
    assert report_reader.validate_header("/my/path/Inforeport_reader.xls") == (
        2019,
        "INSTITUTION",
    )


def test_clean_table_cols() -> None:
    """Return cleaned DataFrame."""
    df = pd.DataFrame(
        {
            "full_valued": [1, 2, 3],
            "all_missing1": [None, None, None],
            "some_missing": [None, 2, 3],
            "all_missing2": [None, None, None],
        }
    )
    expected_df = pd.DataFrame({"full_valued": [1, 2, 3], "some_missing": [None, 2, 3]})
    result_df = report_reader.clean_table_cols(df)
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_get_trades() -> None:
    """Return a list of trade tuples."""
    df = pd.DataFrame(
        {
            "Data": ["10/10/2019", "12/11/2019"],
            "Operação": ["B   ", "S   "],
            "Quantidade": [10, 100],
            "Valor Total (R$)": [102.0, 3050],
        }
    )
    expected_result = [
        ("10/10/2019 B    10 R$ 102,00", 0),
        ("12/11/2019 S    100 R$ 3050,00", 1),
    ]
    result = report_reader.get_trades(df)
    assert expected_result == result


def test_group_trades() -> None:
    """Return a DataFrame of grouped trades."""
    df = pd.DataFrame(
        {
            "Data Negócio": ["1", "1", "2", "2", "2", "2"],
            "Código": ["BOVA11", "PETR4", "PETR4", "BOVA11", "BOVA11", "BOVA11"],
            "C/V": [" C ", " V ", " V ", " V ", " C ", " C "],
            "Quantidade": [20, 30, 50, 80, 130, 210],
            "Valor Total (R$)": [10.20, 30.50, 80.13, 210.34, 550.89, 144.233],
            "Especificação do Ativo": [
                "ISHARES",
                "PETRO",
                "PETRO",
                "ISHARES",
                "ISHARES",
                "ISHARES",
            ],
        }
    )
    expected_df = pd.DataFrame(
        {
            "Data Negócio": ["1", "1", "2", "2", "2"],
            "Código": ["BOVA11", "PETR4", "BOVA11", "BOVA11", "PETR4"],
            "C/V": [" C ", " V ", " C ", " V ", " V "],
            "Quantidade": [20, 30, 340, 80, 50],
            "Valor Total (R$)": [10.20, 30.50, 695.123, 210.34, 80.13],
            "Especificação do Ativo": [
                "ISHARES",
                "PETRO",
                "ISHARES",
                "ISHARES",
                "PETRO",
            ],
        }
    )
    result_df = report_reader.group_trades(df)
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_calculate_taxes_2019(mocker: MockerFixture) -> None:
    """Return calculated taxes."""
    mocker.patch("irpf_investidor.b3.get_trading_rate", return_value=0.000275)
    mocker.patch(
        "irpf_investidor.b3.get_emoluments_rates",
        return_value=[0.00004105, 0.00004105, 0.00004105],
    )
    df = pd.DataFrame(
        {
            "Data Negócio": [
                datetime.datetime(2019, 2, 20),
                datetime.datetime(2019, 3, 6),
                datetime.datetime(2019, 5, 14),
            ],
            "Valor Total (R$)": [935, 10956, 8870],
        }
    )
    expected_df = pd.DataFrame(
        {
            "Data Negócio": [
                datetime.datetime(2019, 2, 20),
                datetime.datetime(2019, 3, 6),
                datetime.datetime(2019, 5, 14),
            ],
            "Valor Total (R$)": [935, 10956, 8870],
            "Liquidação (R$)": [0.25, 3.01, 2.43],
            "Emolumentos (R$)": [0.03, 0.44, 0.36],
        }
    )
    result_df = report_reader.calculate_taxes(df, [])
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_buy_sell_columns() -> None:
    """Return DataFrame with separated buy/sell columns."""
    df = pd.DataFrame(
        {
            "Data Negócio": ["1", "1", "2", "2", "2"],
            "Código": ["BOVA11", "PETR4", "BOVA11", "BOVA11", "PETR4"],
            "C/V": [" C ", " V ", " C ", " V ", " V "],
            "Quantidade": [20, 30, 340, 80, 50],
            "Valor Total (R$)": [10.20, 30.50, 695.123, 210.34, 80.13],
            "Liquidação (R$)": [1, 2, 5, 4, 3],
            "Emolumentos (R$)": [0.2, 0.3, 1.3, 0.8, 0.5],
        }
    )
    expected_df = pd.DataFrame(
        {
            "Data Negócio": ["1", "1", "2", "2", "2"],
            "Código": ["BOVA11", "PETR4", "BOVA11", "BOVA11", "PETR4"],
            "C/V": [" C ", " V ", " C ", " V ", " V "],
            "Liquidação (R$)": [1, 2, 5, 4, 3],
            "Emolumentos (R$)": [0.2, 0.3, 1.3, 0.8, 0.5],
            "Quantidade Compra": [20, 0, 340, 0, 0],
            "Custo Total Compra (R$)": [11.40, 0, 701.423, 0, 0],
            "Quantidade Venda": [0, 30, 0, 80, 50],
            "Custo Total Venda (R$)": [0, 32.80, 0, 215.14, 83.63],
        }
    )
    result_df = report_reader.buy_sell_columns(df)
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_group_buys_sells() -> None:
    """Return a DataFrame with grouped buy/sell trades."""
    df = pd.DataFrame(
        {
            "Código": ["BOVA11", "PETR4", "BOVA11", "BOVA11", "PETR4"],
            "Quantidade Compra": [20, 0, 340, 0, 0],
            "Custo Total Compra (R$)": [11.40, 0, 701.423, 0, 0],
            "Quantidade Venda": [0, 30, 0, 80, 50],
            "Custo Total Venda (R$)": [0, 32.80, 0, 215.14, 83.63],
            "Especificação do Ativo": [
                "ISHARES",
                "PETRO",
                "ISHARES",
                "ISHARES",
                "PETRO",
            ],
        }
    )
    expected_df = pd.DataFrame(
        {
            "Código": ["BOVA11", "PETR4"],
            "Quantidade Compra": [360, 0],
            "Custo Total Compra (R$)": [712.823, 0],
            "Quantidade Venda": [80, 80],
            "Custo Total Venda (R$)": [215.14, 116.43],
            "Especificação do Ativo": ["ISHARES", "PETRO"],
        }
    )
    result_df = report_reader.group_buys_sells(df)
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_average_price() -> None:
    """Return a DataFrame with average price column."""
    df = pd.DataFrame(
        {
            "Código": ["BOVA11", "PETR4"],
            "Quantidade Compra": [360, 0],
            "Custo Total Compra (R$)": [712.823, 0],
        }
    )
    expected_df = pd.DataFrame(
        {
            "Código": ["BOVA11", "PETR4"],
            "Quantidade Compra": [360, 0],
            "Custo Total Compra (R$)": [712.823, 0],
            "Preço Médio (R$)": [1.980064, float("nan")],
        }
    )
    result_df = report_reader.average_price(df)
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_goods_and_rights(
    mocker: MockerFixture,
) -> None:
    """Return a DataFrame."""
    mocker.patch("irpf_investidor.report_reader.buy_sell_columns")
    mocker.patch("irpf_investidor.report_reader.group_buys_sells")
    mocker.patch(
        "irpf_investidor.report_reader.average_price", return_value=pd.DataFrame()
    )

    df = report_reader.goods_and_rights(pd.DataFrame())
    assert type(df) is pd.DataFrame


def test_output_taxes(mocker: MockerFixture) -> None:
    """Print out taxes."""
    mock_print = mocker.patch("builtins.print")

    report_reader.output_taxes(pd.DataFrame())
    mock_print.assert_called_once()


def test_output_goods_and_rights(mocker: MockerFixture) -> None:
    """Print out goods and rights."""
    mocker.patch("irpf_investidor.formatting.get_currency_format")
    mock_print = mocker.patch("builtins.print")

    df = pd.DataFrame(
        {
            "Código": ["BOVA11", "PETR4"],
            "Quantidade Compra": [360, 0],
            "Custo Total Compra (R$)": [712.823, 0],
            "Quantidade Venda": [80, 80],
            "Custo Total Venda (R$)": [215.14, 116.43],
            "Preço Médio (R$)": [1.980, float("nan")],
            "Especificação do Ativo": ["ISHARES", "PETRO"],
        }
    )
    report_reader.output_goods_and_rights(df, 2019, "XYZ")
    assert mock_print.call_count == 3
