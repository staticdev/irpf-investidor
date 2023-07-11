"""Test cases for prompt module."""
import pytest
from pytest_mock import MockerFixture

import irpf_investidor.prompt as prompt

TRADES = [(0, "trade 1"), (0, "trade 2")]


@pytest.fixture
def mock_checkboxlist_dialog(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking shortcuts.checkboxlist_dialog."""
    return mocker.patch("prompt_toolkit.shortcuts.checkboxlist_dialog")


@pytest.fixture
def mock_yes_no_dialog(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking shortcuts.yes_no_dialog."""
    return mocker.patch("prompt_toolkit.shortcuts.yes_no_dialog")


def test_select_trades_empty(
    mock_checkboxlist_dialog: MockerFixture, mock_yes_no_dialog: MockerFixture
) -> None:
    """It returns empty list."""
    mock_checkboxlist_dialog.return_value.run.side_effect = [[], []]
    mock_yes_no_dialog.return_value.run.side_effect = [False, True]

    result = prompt.select_trades(TRADES)

    assert mock_checkboxlist_dialog.call_count == 2
    assert mock_yes_no_dialog.call_count == 2
    assert result == []


def test_select_trades_some_selected(mock_checkboxlist_dialog: MockerFixture) -> None:
    """It returns list with id 1."""
    mock_checkboxlist_dialog.return_value.run.return_value = [1]

    result = prompt.select_trades(TRADES)

    assert result == [1]
