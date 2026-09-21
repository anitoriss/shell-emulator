"""Выполнение стартового скрипта: команды из файла, одна за другой."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from emulator.result import with_newline
from emulator.shell import Shell

ENCODING = "utf-8-sig"
COMMENT = "#"


@dataclass
class ScriptReport:
    """Итог выполнения скрипта.

    Attributes:
        ok: False, если скрипт остановлен из-за ошибки.
        exit_requested: True, если в скрипте была команда exit.
        failed_line: номер строки с ошибкой (нумерация с единицы).
    """

    ok: bool = True
    exit_requested: bool = False
    failed_line: int = 0


def read_script(path: Path) -> list[str]:
    """Прочитать строки скрипта (кодировка UTF-8, BOM допускается)."""
    return path.read_text(encoding=ENCODING).splitlines()


def run_script(
    shell: Shell, path: Path, emit: Callable[[str], None]
) -> ScriptReport:
    """Выполнить скрипт, показывая через emit и ввод, и вывод.

    Пустые строки и строки, начинающиеся с #, пропускаются. Скрипт
    останавливается на первой ошибке или после команды exit.
    """
    for number, raw in enumerate(read_script(path), start=1):
        line = raw.strip()
        if not line or line.startswith(COMMENT):
            continue
        emit(f"{shell.prompt()}{line}\n")
        result = shell.execute(line)
        emit(with_newline(result.output))
        if not result.ok:
            return ScriptReport(ok=False, failed_line=number)
        if result.exit_requested:
            return ScriptReport(exit_requested=True)
    return ScriptReport()
