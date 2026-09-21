"""Данные об операционной системе, в которой запущен эмулятор."""

import getpass
import socket

FALLBACK_USER = "user"


def get_username() -> str:
    """Вернуть имя текущего пользователя ОС."""
    try:
        return getpass.getuser()
    except (ImportError, KeyError, OSError):
        return FALLBACK_USER


def get_hostname() -> str:
    """Вернуть имя компьютера, на котором запущен эмулятор."""
    return socket.gethostname()
