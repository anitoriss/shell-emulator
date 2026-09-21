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
    assert "alice@box$ ls a b" in shown_text(app)
    assert "ls: args=['a', 'b']" in shown_text(app)


def test_error_is_shown(app):
    """Сообщение об ошибке показывается в окне."""
    app.submit("nope")
    assert "nope: command not found" in shown_text(app)
