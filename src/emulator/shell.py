"""Ядро эмулятора: разбор строки и запуск команд."""

from pathlib import Path

from emulator.commands import COMMANDS
from emulator.parser import ParseError, tokenize
from emulator.result import CommandError, Result, failure
from emulator.vfs import Vfs

DEFAULT_PROMPT = "{user}@{host}:{cwd}$ "


class Shell:
    """Интерпретатор команд эмулятора."""

    def __init__(
        self,
        user: str,
        host: str,
        prompt: str = DEFAULT_PROMPT,
        vfs: Vfs | None = None,
        vfs_path: Path | None = None,
    ):
        """Создать оболочку для пользователя user на компьютере host.

        vfs - виртуальная файловая система (по умолчанию встроенная),
        vfs_path - директория на диске, из которой загружена VFS.
        """
        self.user = user
        self.host = host
        self.prompt_template = prompt
        self.vfs = vfs if vfs is not None else Vfs.default()
        self.vfs_path = vfs_path

    def prompt(self) -> str:
        """Вернуть приглашение к вводу с подставленными значениями."""
        text = self.prompt_template.replace("{user}", self.user)
        text = text.replace("{host}", self.host)
        return text.replace("{cwd}", self.vfs.pwd())

    def execute(self, line: str) -> Result:
        """Выполнить одну строку и вернуть результат."""
        try:
            tokens = tokenize(line)
        except ParseError as error:
            return failure(f"syntax error: {error}")
        if not tokens:
            return Result()
        name, args = tokens[0], tokens[1:]
        handler = COMMANDS.get(name)
        if handler is None:
            return failure(f"{name}: command not found")
        try:
            return handler(self, args)
        except CommandError as error:
            return failure(str(error))
