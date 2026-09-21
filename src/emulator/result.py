"""Результат выполнения команды и общие вспомогательные функции."""

from dataclasses import dataclass


class CommandError(Exception):
    """Ошибка команды; текст ошибки показывается пользователю."""


@dataclass
class Result:
    """Итог выполнения одной команды.

    Attributes:
        output: текст, который нужно показать пользователю.
        ok: False, если команда завершилась ошибкой.
        exit_requested: True, если нужно завершить эмулятор.
    """

    output: str = ""
    ok: bool = True
    exit_requested: bool = False


def failure(message: str) -> Result:
    """Создать результат-ошибку с сообщением message."""
    return Result(output=message, ok=False)


def with_newline(text: str) -> str:
    """Добавить перевод строки в конец непустого текста, если его нет."""
    if not text or text.endswith("\n"):
        return text
    return text + "\n"
