"""Тесты ядра эмулятора: выполнение строк, ошибки, exit."""

import pytest

from emulator.shell import Shell


@pytest.fixture
def shell():
    """Вернуть оболочку для пользователя alice на компьютере box."""
    return Shell("alice", "box")


def test_prompt_uses_user_and_host(shell):
    """Приглашение по умолчанию содержит имя пользователя и хоста."""
    assert shell.prompt() == "alice@box:/$ "


def test_unknown_command_is_error(shell):
    """Неизвестная команда даёт ошибку command not found."""
    result = shell.execute("frobnicate 1 2")
    assert not result.ok
    assert result.output == "frobnicate: command not found"


def test_parse_error_is_reported(shell):
    """Незакрытая кавычка сообщается как синтаксическая ошибка."""
    result = shell.execute('ls "oops')
    assert not result.ok
    assert result.output.startswith("syntax error")


def test_empty_line_does_nothing(shell):
    """Пустая строка не выводит ничего и не считается ошибкой."""
    result = shell.execute("   ")
    assert result.ok
    assert result.output == ""


def test_exit_requests_shutdown(shell):
    """Команда exit просит завершить эмулятор."""
    assert shell.execute("exit").exit_requested


def test_exit_with_arguments_is_error(shell):
    """Команда exit с аргументами - ошибка, эмулятор не закрывается."""
    result = shell.execute("exit now")
    assert not result.ok
    assert not result.exit_requested
