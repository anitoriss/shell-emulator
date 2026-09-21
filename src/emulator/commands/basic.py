"""Базовые команды: exit и заглушки ls и cd."""

from emulator.result import CommandError, Result


def _stub(name: str, args: list[str]) -> Result:
    """Вернуть результат-заглушку с именем команды и аргументами."""
    return Result(f"{name}: args={args}")


def cmd_ls(shell, args: list[str]) -> Result:
    """Заглушка ls: печатает своё имя и аргументы."""
    return _stub("ls", args)


def cmd_cd(shell, args: list[str]) -> Result:
    """Заглушка cd: печатает своё имя и аргументы."""
    return _stub("cd", args)


def cmd_exit(shell, args: list[str]) -> Result:
    """Завершить работу эмулятора."""
    if args:
        raise CommandError("exit: too many arguments")
    return Result(exit_requested=True)
