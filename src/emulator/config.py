"""Параметры командной строки эмулятора."""

import argparse
from dataclasses import dataclass
from pathlib import Path

from emulator.shell import DEFAULT_PROMPT

NOT_SET = "<not set>"


def existing_file(value: str) -> Path:
    """Проверить, что value - путь к существующему файлу."""
    path = Path(value)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"file not found: {value}")
    return path


def _shown(value) -> str:
    """Показать значение параметра для отладочного вывода."""
    if value is None:
        return NOT_SET
    return repr(str(value))


@dataclass
class Config:
    """Настройки эмулятора, заданные в командной строке."""

    vfs_path: Path | None = None
    prompt: str = DEFAULT_PROMPT
    script_path: Path | None = None

    def describe(self) -> list[str]:
        """Вернуть строки отладочного вывода со всеми параметрами."""
        return [
            "[debug] --vfs    = " + _shown(self.vfs_path),
            "[debug] --prompt = " + _shown(self.prompt),
            "[debug] --script = " + _shown(self.script_path),
        ]


def build_parser() -> argparse.ArgumentParser:
    """Создать разборщик параметров командной строки."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Эмулятор оболочки ОС с виртуальной файловой системой.",
    )
    parser.add_argument(
        "--vfs", type=Path, metavar="PATH",
        help="путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT, metavar="TEXT",
        help="приглашение; можно использовать {user}, {host}, {cwd}",
    )
    parser.add_argument(
        "--script", type=existing_file, metavar="PATH",
        help="путь к стартовому скрипту с командами эмулятора",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> Config:
    """Разобрать параметры argv (по умолчанию - sys.argv[1:])."""
    namespace = build_parser().parse_args(argv)
    return Config(
        vfs_path=namespace.vfs,
        prompt=namespace.prompt,
        script_path=namespace.script,
    )
