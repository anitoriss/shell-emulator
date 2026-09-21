"""Ядро эмулятора: разбор строки и запуск команд."""

from emulator.commands import COMMANDS
from emulator.parser import ParseError, tokenize
from emulator.result import CommandError, Result, failure

DEFAULT_PROMPT = "{user}@{host}$ "


class Shell:
    """Интерпретатор команд эмулятора."""

    def __init__(self, user: str, host: str, prompt: str = DEFAULT_PROMPT):
        """Создать оболочку для пользователя user на компьютере host."""
        self.user = user
        self.host = host
        self.prompt_template = prompt

    def prompt(self) -> str:
        """Вернуть приглашение к вводу с подставленными значениями."""
        text = self.prompt_template.replace("{user}", self.user)
        return text.replace("{host}", self.host)

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
