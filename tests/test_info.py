"""Тесты команд uptime и who."""

import re
from datetime import datetime

import pytest

from emulator.commands.info import format_uptime
from emulator.shell import Shell

MINUTE = 60
HOUR = 3600
DAY = 86400


@pytest.fixture
def shell():
    """Вернуть оболочку, запущенную три минуты назад."""
    instance = Shell("alice", "box")
    instance.started_at -= 3 * MINUTE
    return instance


@pytest.mark.parametrize("seconds, expected", [
    (0, "0 min"),
    (3 * MINUTE + 5, "3 min"),
    (HOUR + 5 * MINUTE, "1:05"),
    (DAY + HOUR, "1 day, 1:00"),
    (2 * DAY + 3 * HOUR + 4 * MINUTE, "2 days, 3:04"),
])
def test_format_uptime(seconds, expected):
    """Время работы оформляется как в настоящей команде uptime."""
    assert format_uptime(seconds) == expected


def test_uptime_output(shell):
    """Команда uptime печатает время, аптайм, пользователей и нагрузку."""
    result = shell.execute("uptime")
    assert result.ok
    pattern = (
        r" \d\d:\d\d:\d\d up 3 min,  1 user,  "
        r"load average: 0\.00, 0\.00, 0\.00"
    )
    assert re.fullmatch(pattern, result.output)


def test_uptime_rejects_arguments(shell):
    """Команда uptime с аргументами - ошибка."""
    result = shell.execute("uptime -p")
    assert not result.ok
    assert result.output == "uptime: unexpected argument '-p'"


def test_who_output(shell):
    """Команда who печатает пользователя, терминал, время входа и хост."""
    result = shell.execute("who")
    login = datetime.fromtimestamp(shell.started_at).strftime("%Y-%m-%d %H:%M")
    assert result.ok
    assert result.output == f"alice  pts/0  {login} (box)"


def test_who_rejects_arguments(shell):
    """Команда who с аргументами - ошибка."""
    result = shell.execute("who am i")
    assert not result.ok
    assert result.output == "who: extra operand 'am'"
