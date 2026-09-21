"""Тесты параметров командной строки."""

import pytest

from emulator.config import Config, parse_args
from emulator.shell import DEFAULT_PROMPT

USAGE_ERROR_CODE = 2


def test_defaults():
    """Без параметров используются значения по умолчанию."""
    config = parse_args([])
    assert config == Config(None, DEFAULT_PROMPT, None)


def test_all_parameters(tmp_path):
    """Все три параметра попадают в конфигурацию."""
    script = tmp_path / "start.txt"
    script.write_text("exit\n")
    config = parse_args([
        "--vfs", str(tmp_path), "--prompt", "demo> ",
        "--script", str(script),
    ])
    assert config.vfs_path == tmp_path
    assert config.prompt == "demo> "
    assert config.script_path == script


def test_missing_script_is_usage_error(tmp_path, capsys):
    """Несуществующий скрипт - ошибка параметров с кодом 2."""
    missing = tmp_path / "nope.txt"
    with pytest.raises(SystemExit) as info:
        parse_args(["--script", str(missing)])
    assert info.value.code == USAGE_ERROR_CODE
    assert "file not found" in capsys.readouterr().err


def test_describe_lists_every_parameter():
    """Отладочный вывод содержит все три параметра."""
    lines = Config(prompt="> ").describe()
    assert lines == [
        "[debug] --vfs    = <not set>",
        "[debug] --prompt = '> '",
        "[debug] --script = <not set>",
    ]
