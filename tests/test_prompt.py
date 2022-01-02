"""Test cases for prompt module."""
from pytest_mock import MockerFixture

import irpf_investidor.prompt as prompt


def test_select_trades_empty(mocker: MockerFixture) -> None:
    """It returns empty list."""
    mocker.patch(
        "inquirer.prompt",
        side_effect=[{"trades": []}, {"": "Não"}, {"trades": []}, {"": "Sim"}],
    )
    trades = [("trade 1", 0), ("trade 2", 1)]
    assert prompt.select_trades(trades) == []


def test_select_trades_some_selected(mocker: MockerFixture) -> None:
    """It returns list with id 1."""
    mocker.patch("inquirer.prompt", return_value={"trades": [1]})
    trades = [("trade 1", 0), ("trade 2", 1)]
    assert prompt.select_trades(trades) == [1]
