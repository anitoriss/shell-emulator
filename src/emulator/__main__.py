"""Точка входа: python -m emulator [--vfs] [--prompt] [--script]."""

import sys
from pathlib import Path

from emulator.config import parse_args
from emulator.gui import App
from emulator.shell import Shell
from emulator.sysinfo import get_hostname, get_username
from emulator.vfs import Vfs, VfsError

EXIT_VFS_ERROR = 2


def configure_stdout():
    """Не падать при печати символов, которых нет в кодировке консоли."""
    stream = sys.stdout
    if stream is not None and hasattr(stream, "reconfigure"):
        stream.reconfigure(errors="replace")


def load_vfs(path: Path | None) -> Vfs:
    """Загрузить VFS из директории path или создать VFS по умолчанию."""
    if path is None:
        return Vfs.default()
    return Vfs.from_directory(path)


def main(argv: list[str] | None = None) -> int:
    """Разобрать параметры, загрузить VFS и запустить окно эмулятора."""
    configure_stdout()
    config = parse_args(argv)
    try:
        vfs = load_vfs(config.vfs_path)
    except VfsError as error:
        print(f"emulator: error: {error}", file=sys.stderr)
        return EXIT_VFS_ERROR
    shell = Shell(
        get_username(), get_hostname(), config.prompt, vfs, config.vfs_path
    )
    app = App(shell)
    debug_lines = config.describe() + [f"[debug] VFS loaded: {vfs.stats()}"]
    for line in debug_lines:
        print(line)
    app.show_lines(debug_lines)
    if config.script_path is not None:
        app.start_script(config.script_path)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
