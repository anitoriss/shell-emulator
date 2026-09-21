"""Точка входа: python -m emulator."""

import sys

from emulator.gui import App
from emulator.shell import Shell
from emulator.sysinfo import get_hostname, get_username


def main() -> int:
    """Создать оболочку и запустить окно эмулятора."""
    shell = Shell(get_username(), get_hostname())
    App(shell).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
