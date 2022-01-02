"""Command-line interface."""
from __future__ import annotations

import click

import irpf_investidor.formatting
import irpf_investidor.prompt as prompt
import irpf_investidor.report_reader


@click.command()
@click.version_option()
def main() -> None:
    """Sequecence of operations for trades."""
    response = irpf_investidor.formatting.set_pt_br_locale()
    if not response:
        click.secho(
            f"Erro: {response.value['message']}",
            fg="red",
            err=True,
        )
        # Raises SystemExit
        raise click.ClickException("")
    filename = irpf_investidor.report_reader.get_xls_filename()
    click.secho(f"Nome do arquivo: {filename}", fg="blue")

    ref_year, institution = irpf_investidor.report_reader.validate_header(filename)
    source_df = irpf_investidor.report_reader.read_xls(filename)
    source_df = irpf_investidor.report_reader.clean_table_cols(source_df)
    source_df = irpf_investidor.report_reader.group_trades(source_df)
    trades = irpf_investidor.report_reader.get_trades(source_df)
    auction_trades = prompt.select_trades(trades)
    tax_df = irpf_investidor.report_reader.calculate_taxes(source_df, auction_trades)
    irpf_investidor.report_reader.output_taxes(tax_df)
    result_df = irpf_investidor.report_reader.goods_and_rights(tax_df)
    irpf_investidor.report_reader.output_goods_and_rights(
        result_df, ref_year, institution
    )


if __name__ == "__main__":
    main()  # pragma: no cover
