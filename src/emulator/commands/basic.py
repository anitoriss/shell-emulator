"""Базовые команды: exit."""

from emulator.result import CommandError, Result


def cmd_exit(shell, args: list[str]) -> Result:
    """Завершить работу эмулятора."""
    if args:
        raise CommandError("exit: too many arguments")
    return Result(exit_requested=True)
