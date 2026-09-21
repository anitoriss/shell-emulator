"""Дымовые тесты окна (пропускаются, если нет графического дисплея)."""

import tkinter as tk

import pytest

from emulator.gui import App
from emulator.shell import Shell


@pytest.fixture
def app():
    """Создать окно эмулятора или пропустить тест без дисплея."""
    try:
        instance = App(Shell("alice", "box"))
    except tk.TclError:
        pytest.skip("нет дисплея для tkinter")
    yield instance
    try:
        instance.root.destroy()
    except tk.TclError:
        pass


def shown_text(app):
    """Вернуть весь текст из области вывода."""
    return app.output.get("1.0", tk.END)


def test_title_is_built_from_os_data(app):
    """Заголовок окна имеет вид «Эмулятор - [пользователь@хост]»."""
    assert app.root.title() == "Эмулятор - [alice@box]"


def test_submit_echoes_command_and_output(app):
    """Введённая команда и её вывод появляются в области вывода."""
    app.submit("ls a b")
    assert "alice@box:/$ ls a b" in shown_text(app)
    assert "ls: args=['a', 'b']" in shown_text(app)


def test_error_is_shown(app):
    """Сообщение об ошибке показывается в окне."""
    app.submit("nope")
    assert "nope: command not found" in shown_text(app)


def test_show_lines_writes_debug_output(app):
    """Служебные строки отображаются в области вывода."""
    app.show_lines(["[debug] --vfs = <not set>"])
    assert "[debug] --vfs = <not set>" in shown_text(app)


def test_startup_script_dialog_is_shown(app, tmp_path):
    """Стартовый скрипт показывается как диалог: ввод и вывод."""
    script = tmp_path / "start.txt"
    script.write_text("ls x\n", encoding="utf-8")
    app.run_startup(script)
    assert "alice@box:/$ ls x" in shown_text(app)
    assert "ls: args=['x']" in shown_text(app)


def test_startup_script_error_is_reported(app, tmp_path):
    """Остановка скрипта из-за ошибки отмечается в окне."""
    script = tmp_path / "start.txt"
    script.write_text("nope\nls\n", encoding="utf-8")
    app.run_startup(script)
    assert "[script] stopped: error on line 1" in shown_text(app)
