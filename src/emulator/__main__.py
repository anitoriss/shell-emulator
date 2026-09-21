"""Точка входа: python -m emulator [--vfs] [--prompt] [--script]."""

import sys

from emulator.config import parse_args
from emulator.gui import App
from emulator.shell import Shell
from emulator.sysinfo import get_hostname, get_username


def configure_stdout():
    """Не падать при печати символов, которых нет в кодировке консоли."""
    stream = sys.stdout
    if stream is not None and hasattr(stream, "reconfigure"):
        stream.reconfigure(errors="replace")


def main(argv: list[str] | None = None) -> int:
    """Разобрать параметры, показать их и запустить окно эмулятора."""
    configure_stdout()
    config = parse_args(argv)
    shell = Shell(get_username(), get_hostname(), config.prompt)
    app = App(shell)
    debug_lines = config.describe()
    for line in debug_lines:
        print(line)
    app.show_lines(debug_lines)
    if config.script_path is not None:
        app.start_script(config.script_path)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
