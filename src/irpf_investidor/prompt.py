"""Prompt module."""
from typing import Any

import inquirer


def select_trades(trades: list[tuple[str, int]]) -> Any:
    """Checkbox selection of auction trades.

    Args:
        trades (list[tuple[str, int]]): list of all trades and indexes.

    Returns:
        Any: list of indexes of selected auction trades.
    """
    while True:
        selection = inquirer.prompt(
            [
                inquirer.Checkbox(
                    "trades",
                    message=(
                        "Quais operações foram realizadas em horário de leilão? "
                        "(Selecione apertando espaço e ao terminar aperte enter)"
                    ),
                    choices=trades,
                )
            ]
        )["trades"]
        if len(selection) == 0:
            answer = inquirer.prompt(
                [
                    inquirer.List(
                        "",
                        message="Nenhuma operação selecionada.\nIsso está correto?",
                        choices=["Sim", "Não"],
                    )
                ]
            )[""]
            if answer == "Sim":
                return []
        else:
            return selection
