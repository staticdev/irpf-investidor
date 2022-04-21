"""Report reader."""
from __future__ import annotations

import datetime
import glob
import math
import os
import sys

import pandas as pd
import xlrd

import irpf_investidor.b3
import irpf_investidor.formatting


IRPF_INVESTIMENT_CODES = {
    "ETF": "74 (ETF)",
    "FII": "73 (FII)",
    "STOCKS": "31 (Ações)",
    "NOT_FOUND": "Não encontrado",
}
FIRST_IMPLEMENTED_YEAR = 2019
LAST_IMPLEMENTED_YEAR = 2021


def get_xls_filename() -> str:
    """Return first xls filename in current folder or Downloads folder."""
    filenames = glob.glob("InfoCEI*.xls")
    if filenames:
        return filenames[0]
    home = os.path.expanduser("~")
    filenames = glob.glob(os.path.join(home, "Downloads", "InfoCEI*.xls"))
    if filenames:
        return filenames[0]
    return sys.exit(
        "Erro: arquivo não encontrado, confira a documentação para mais informações."
    )


def date_parse(value: str) -> datetime.datetime:
    """Parse dates from CEI report."""
    return datetime.datetime.strptime(value.strip(), "%d/%m/%y")


def validate_period(first: str, second: str) -> int:
    """Consider the year from the first trade date."""
    first_year = int(first[-4:])
    second_year = int(second[-4:])
    if (
        first_year <= second_year
        and first_year >= FIRST_IMPLEMENTED_YEAR
        and second_year <= LAST_IMPLEMENTED_YEAR
    ):
        return second_year
    return sys.exit(
        f"Erro: o período de {first} a {second} não é válido, favor verificar "
        "instruções na documentação."
    )


def validate_header(filepath: str) -> tuple[int, str]:
    """Validate file header.

    Arguments:
        filepath: CEI report's full path

    Returns:
        Tuple[int, str]: reference year for the report and institution name if valid.
    """
    try:
        basic_df = pd.read_excel(
            filepath,
            usecols="B",
            date_parser=date_parse,
            skiprows=4,
        )
    # exits if empty
    except (ValueError, xlrd.XLRDError):
        sys.exit(
            f"Erro: arquivo {filepath} não se encontra íntegro ou no formato de "
            "relatórios do CEI."
        )

    periods = basic_df["Período de"].iloc[0].split(" a ")
    ref_year = validate_period(periods[0], periods[1])

    instutition = basic_df["Período de"].iloc[4]
    return ref_year, instutition


def read_xls(filename: str) -> pd.DataFrame:
    """Read xls.

    Args:
        filename (str): name of XLS file.

    Returns:
        pd.DataFrame: content of the file.
    """
    df = pd.read_excel(
        filename,
        usecols="B:K",
        parse_dates=["Data Negócio"],
        date_parser=date_parse,
        skipfooter=4,
        skiprows=10,
    )
    return df


# Source: https://realpython.com/python-rounding/
def round_down_money(n: float, decimals: int = 2) -> float:
    """Round float on second decimal cases.

    Args:
        n (float): number.
        decimals (int): Number of decimal cases. Defaults to 2.

    Returns:
        float: rounded number.
    """
    multiplier = 10**decimals
    # Type-hint for floor won't work until Python 3.9
    # https://github.com/python/typeshed/issues/3195
    return math.floor(n * multiplier) / multiplier  # type: ignore


def clean_table_cols(source_df: pd.DataFrame) -> pd.DataFrame:
    """Drop columns without values.

    Args:
        source_df (pd.DataFrame): full columns DataFrame.

    Returns:
        pd.DataFrame: DataFrame without columns with no value.
    """
    return source_df.dropna(axis="columns", how="all")


def get_trades(df: pd.DataFrame) -> list[tuple[int, str]]:
    """Return trades representations.

    Args:
        df (pd.DataFrame): trades DataFrame.

    Returns:
        trades: list of df indexes and string representations.
    """
    df["total_cost_rs"] = df["Valor Total (R$)"].apply(
        lambda x: "R$ " + str(f"{x:.2f}".replace(".", ","))
    )
    df = df.drop(columns=["Valor Total (R$)"])
    list_of_list = df.astype(str).values.tolist()
    df = df.drop(columns=["total_cost_rs"])
    return [(i, " ".join(x)) for i, x in enumerate(list_of_list)]


def group_trades(df: pd.DataFrame) -> pd.DataFrame:
    """Group trades by day, asset and action.

    Args:
        df (pd.DataFrame): ungrouped trades.

    Returns:
        pd.DataFrame: grouped trades.
    """
    return (
        df.groupby(["Data Negócio", "Código", "C/V"])
        .agg(
            {
                "Quantidade": "sum",
                "Valor Total (R$)": "sum",
                "Especificação do Ativo": "first",
            }
        )
        .reset_index()
    )


def calculate_taxes(df: pd.DataFrame, auction_trades: list[int]) -> pd.DataFrame:
    """Calculate emolumentos and liquidação taxes based on reference year.

    Args:
        df: grouped trades.
        auction_trades: list of auction trades.

    Returns:
        pd.DataFrame: trades with two new columns of calculated taxes.
    """
    df["Liquidação (R$)"] = (
        df["Valor Total (R$)"]
        * irpf_investidor.b3.get_liquidacao_rates(df["Data Negócio"].array)
    ).apply(round_down_money)
    df["Emolumentos (R$)"] = (
        df["Valor Total (R$)"]
        * irpf_investidor.b3.get_emolumentos_rates(
            df["Data Negócio"].array, auction_trades
        )
    ).apply(round_down_money)
    return df


def buy_sell_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Create columns for buys and sells with quantity and total value.

    Args:
        df (pd.DataFrame): grouped trades.

    Returns:
        pd.DataFrame: grouped trades with four new columns of buys and sells.
    """
    df["Quantidade Compra"] = df["Quantidade"].where(df["C/V"].str.contains("C"), 0)
    df["Custo Total Compra (R$)"] = (
        df[["Valor Total (R$)", "Liquidação (R$)", "Emolumentos (R$)"]]
        .sum(axis="columns")
        .where(df["C/V"].str.contains("C"), 0)
    ).round(decimals=2)
    df["Quantidade Venda"] = df["Quantidade"].where(df["C/V"].str.contains("V"), 0)
    df["Custo Total Venda (R$)"] = (
        df[["Valor Total (R$)", "Liquidação (R$)", "Emolumentos (R$)"]]
        .sum(axis="columns")
        .where(df["C/V"].str.contains("V"), 0)
    ).round(decimals=2)
    df.drop(["Quantidade", "Valor Total (R$)"], axis="columns", inplace=True)
    return df


def group_buys_sells(df: pd.DataFrame) -> pd.DataFrame:
    """Group buys and sells by asset.

    Args:
        df (pd.DataFrame): ungrouped buys and sells.

    Returns:
        pd.DataFrame: grouped buys and sells.
    """
    return (
        df.groupby(["Código"])
        .agg(
            {
                "Quantidade Compra": "sum",
                "Custo Total Compra (R$)": "sum",
                "Quantidade Venda": "sum",
                "Custo Total Venda (R$)": "sum",
                "Especificação do Ativo": "first",
            }
        )
        .round(decimals=2)
        .reset_index()
    )


def average_price(df: pd.DataFrame) -> pd.DataFrame:
    """Compute average price.

    Args:
        df (pd.DataFrame): buys and sells without average price.

    Returns:
        pd.DataFrame: buys and sells with average price.
    """
    df["Preço Médio (R$)"] = df["Custo Total Compra (R$)"] / df["Quantidade Compra"]
    return df


def goods_and_rights(source_df: pd.DataFrame) -> pd.DataFrame:
    """Call methods for goods and rights.

    Args:
        source_df (pd.DataFrame): raw DataFrame.

    Returns:
        pd.DataFrame: goods and rights DataFrame.
    """
    result_df = buy_sell_columns(source_df)
    result_df = group_buys_sells(source_df)
    result_df = average_price(result_df)
    return result_df


def output_taxes(tax_df: pd.DataFrame) -> None:
    """Print tax DataFrame.

    Args:
        tax_df (pd.DataFrame): calculated tax columns.
    """
    with pd.option_context("display.max_rows", None, "display.max_columns", None):
        print("Valores calculados de emolumentos, liquidação e custo total:\n", tax_df)


def output_goods_and_rights(
    result_df: pd.DataFrame, ref_year: int, institution: str
) -> None:
    """Return a list of assets."""
    pd.set_option("float_format", irpf_investidor.formatting.get_currency_format())
    print("========= Bens e Direitos =========")
    for row in result_df.iterrows():
        idx = row[0]
        content = row[1]
        desc = content["Especificação do Ativo"]
        code = content["Código"]
        qtd = content["Quantidade Compra"] - content["Quantidade Venda"]
        avg_price = content["Preço Médio (R$)"]
        avg_price_str = irpf_investidor.formatting.fmt_money(avg_price, 3)
        cnpj = irpf_investidor.b3.get_cnpj_institution(institution)
        result = irpf_investidor.formatting.fmt_money(avg_price * qtd, 2)
        asset_info = irpf_investidor.b3.get_asset_info(code)
        print(
            f"============= Ativo {idx + 1} =============\n"
            f"Código: {IRPF_INVESTIMENT_CODES[asset_info.category]}\n"
            f"CNPJ: {asset_info.cnpj if asset_info.cnpj else 'Não encontrado'}\n"
            f"Discriminação (sugerida): {desc}, código: {code}, quantidade: {qtd}, "
            f"preço médio de compra: R$ {avg_price_str}, corretora: {institution} -"
            f" CNPJ {cnpj}\nSituação em 31/12/{ref_year}: R$ {result}\n"
        )
