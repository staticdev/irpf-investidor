"""Prompt module."""
from __future__ import annotations

import prompt_toolkit.shortcuts as shortcuts


TITLE = "IRPF Investidor"


def select_trades(trades: list[tuple[int, str]]) -> list[int]:
    """Checkbox selection of auction trades.

    Args:
        trades: list of all trades and indexes.

    Returns:
        list of string indexes of selected auction trades.
    """
    text = (
        "Informe as operações realizadas em horário de leilão para cálculo dos "
        "emolumentos.\nEssa informação é obtida através de sua corretora."
    )
    while True:
        operations: list[int] = shortcuts.checkboxlist_dialog(
            title=TITLE,
            text=text,
            values=trades,
        ).run()
        if not operations or len(operations) == 0:
            confirmed = shortcuts.yes_no_dialog(
                title=TITLE, text="Nenhuma operação selecionada.\nIsso está correto?"
            ).run()
            if confirmed:
                return []
        else:
            return operations
