import io
import sys
import builtins
import pytest
from unittest.mock import patch

from sut.tui import TUI, Style

# from your_module import TUI, Style

@pytest.fixture
def tui(monkeypatch):
    t_builtin_print_backup = builtins.print

    # fresh TUI, but do NOT override builtins.print
    if hasattr(builtins, "tui"):
        del builtins.tui
    t = TUI(prompt="TEST> ")
    builtins.print = t_builtin_print_backup
    yield t

def test_print_defaults_to_reset(tui, capsys):
    tui.print("Hello")  # writes via builtins.print override
    captured = capsys.readouterr()
    assert "Hello" in captured.out
    assert "TEST> " in captured.out
    assert "\033[0m" in captured.out

def test_print_with_styles(tui, capsys):
    tui.print("Error", Style.RED, Style.BOLD)
    output = capsys.readouterr()
    assert "\033[91m" in output.out  # RED
    assert "\033[1m" in output.out   # BOLD
    assert "Error" in output.out

def test_print_no_styles_provided(tui, capsys):
    tui.print("Normal")
    output = capsys.readouterr()
    assert "\033[0m" in output.out
    assert "Normal" in output.out

@pytest.mark.parametrize("input_value,expected", [
    ("", True),
    ("", False),
    ("yes", True),
    ("n", False),
])
def test_input_bool(monkeypatch, tui, input_value, expected):
    # Choose correct default based on test case
    default = expected if input_value == "" else not expected
    monkeypatch.setattr("builtins.input", lambda _: input_value)
    result = tui.input_bool("Continue?", default=default)
    assert result == expected

def test_input_poll_returns_line(monkeypatch, tui):
    fake_input = io.StringIO("line1\n")
    monkeypatch.setattr(sys, "stdin", fake_input)

    # patch select.select to simulate ready stdin
    with patch("select.select", return_value=([sys.stdin], [], [])):
        line = tui.input_poll()
    assert line == "line1"

def test_input_poll_no_input_returns_none(monkeypatch, tui):
    with patch("select.select", return_value=([], [], [])):
        line = tui.input_poll()
    assert line is None

def test_print_clears_line(tui, capsys):
    sys.stdout.write("Old line")
    tui.print("New line")
    output = capsys.readouterr()
    out = output.out

    # The clear line sequence should appear *before* "New line"
    assert "\r\033[K" in out
    assert "New line" in out

def test_multiple_styles_combined(tui, capsys):
    tui.print("Multi", Style.RED, Style.UNDERLINE, Style.BOLD)
    output = capsys.readouterr()
    out = output.out
    assert "\033[91m" in out
    assert "\033[1m" in out
    assert "\033[4m" in out
    assert "Multi" in out

def test_overwrite_warning(monkeypatch):
    # Pre-set a tui to trigger warning
    class Dummy:
        pass
    builtins.tui = Dummy()

    with pytest.warns(UserWarning, match="Overwriting builtin 'tui'"):
        tui_instance = TUI()
    assert builtins.tui is tui_instance