"""Информационные команды: uptime и who."""

import time
from datetime import datetime

from emulator.result import CommandError, Result

SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24
SINGULAR = 1
TERMINAL = "pts/0"
LOAD_AVERAGE = "0.00, 0.00, 0.00"
CLOCK_FORMAT = "%H:%M:%S"
LOGIN_FORMAT = "%Y-%m-%d %H:%M"


def _plural_day(days: int) -> str:
    """Вернуть «day» или «days» в зависимости от количества."""
    return "day" if days == SINGULAR else "days"


def format_uptime(seconds: float) -> str:
    """Оформить время работы как в uptime: «3 min», «1:05», «2 days, 3:04»."""
    minutes = int(seconds // SECONDS_PER_MINUTE)
    hours, minutes = divmod(minutes, MINUTES_PER_HOUR)
    days, hours = divmod(hours, HOURS_PER_DAY)
    clock = f"{hours}:{minutes:02d}" if (days or hours) else f"{minutes} min"
    if days:
        return f"{days} {_plural_day(days)}, {clock}"
    return clock


def cmd_uptime(shell, args: list[str]) -> Result:
    """Показать время, сколько работает эмулятор (uptime)."""
    if args:
        raise CommandError(f"uptime: unexpected argument '{args[0]}'")
    now = datetime.now().strftime(CLOCK_FORMAT)
    up = format_uptime(time.time() - shell.started_at)
    return Result(f" {now} up {up},  1 user,  load average: {LOAD_AVERAGE}")


def cmd_who(shell, args: list[str]) -> Result:
    """Показать, кто работает в системе (who): пользователь и вход."""
    if args:
        raise CommandError(f"who: extra operand '{args[0]}'")
    started = datetime.fromtimestamp(shell.started_at)
    login = started.strftime(LOGIN_FORMAT)
    return Result(f"{shell.user}  {TERMINAL}  {login} ({shell.host})")
