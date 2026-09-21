"""Тесты выполнения стартового скрипта."""

import pytest

from emulator.script import run_script
from emulator.shell import Shell

SECOND_LINE = 2


@pytest.fixture
def shell():
    """Вернуть оболочку с коротким приглашением."""
    return Shell("alice", "box", prompt="> ")


def run(shell, tmp_path, text):
    """Выполнить скрипт с текстом text и вернуть (отчёт, вывод)."""
    script = tmp_path / "start.txt"
    script.write_text(text, encoding="utf-8")
    chunks = []
    report = run_script(shell, script, chunks.append)
    return report, "".join(chunks)


def test_input_and_output_are_shown(shell, tmp_path):
    """На экран попадают и введённая команда, и её вывод."""
    report, shown = run(shell, tmp_path, "ls /\ncd /home\nls\n")
    assert report.ok
    assert shown == "> ls /\netc  home  tmp\n> cd /home\n> ls\nuser\n"


def test_comments_and_blank_lines_are_skipped(shell, tmp_path):
    """Комментарии и пустые строки не выполняются и не показываются."""
    _, shown = run(shell, tmp_path, "# note\n\n  \nls\n")
    assert shown == "> ls\netc  home  tmp\n"


def test_stops_at_first_error(shell, tmp_path):
    """После первой ошибки остальные строки не выполняются."""
    text = "ls /\nbad-command\nls /tmp\n"
    report, shown = run(shell, tmp_path, text)
    assert not report.ok
    assert report.failed_line == SECOND_LINE
    assert "> ls /tmp" not in shown
    assert "bad-command: command not found" in shown


def test_exit_stops_script(shell, tmp_path):
    """Команда exit завершает скрипт и просит закрыть эмулятор."""
    report, shown = run(shell, tmp_path, "ls\nexit\nls /tmp\n")
    assert report.ok
    assert report.exit_requested
    assert "> ls /tmp" not in shown


def test_bom_is_accepted(shell, tmp_path):
    """Файл с BOM (Блокнот Windows) читается корректно."""
    script = tmp_path / "bom.txt"
    script.write_bytes("\ufeffls\n".encode("utf-8"))
    chunks = []
    report = run_script(shell, script, chunks.append)
    assert report.ok
    assert "".join(chunks).startswith("> ls")
