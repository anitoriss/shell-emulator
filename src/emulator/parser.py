"""Разбор строки команды на слова с поддержкой кавычек и экранирования."""

SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
QUOTES = (SINGLE_QUOTE, DOUBLE_QUOTE)
BACKSLASH = "\\"
ESCAPABLE_IN_DOUBLE = (DOUBLE_QUOTE, BACKSLASH)


class ParseError(ValueError):
    """Строку невозможно разобрать (например, не закрыта кавычка)."""


class Lexer:
    """Конечный автомат, превращающий строку в список слов."""

    def __init__(self, line: str):
        """Подготовить разбор строки line."""
        self.line = line
        self.tokens: list[str] = []
        self.buffer: list[str] = []
        self.started = False
        self.quote = ""

    def run(self) -> list[str]:
        """Разобрать всю строку и вернуть список слов."""
        chars = iter(self.line)
        for char in chars:
            self._step(char, chars)
        if self.quote:
            raise ParseError("unterminated quote")
        self._flush()
        return self.tokens

    def _step(self, char, chars):
        """Обработать один символ в зависимости от текущего состояния."""
        if char == BACKSLASH and self.quote != SINGLE_QUOTE:
            self._escape(chars)
        elif self.quote:
            self._in_quotes(char)
        elif char in QUOTES:
            self.quote = char
            self.started = True
        elif char.isspace():
            self._flush()
        else:
            self._add(char)

    def _escape(self, chars):
        """Обработать символ после обратной косой черты."""
        following = next(chars, None)
        if following is None:
            raise ParseError("trailing backslash")
        if self.quote and following not in ESCAPABLE_IN_DOUBLE:
            self._add(BACKSLASH)
        self._add(following)

    def _in_quotes(self, char):
        """Обработать символ внутри кавычек."""
        if char == self.quote:
            self.quote = ""
        else:
            self._add(char)

    def _add(self, char):
        """Добавить символ в текущее слово."""
        self.buffer.append(char)
        self.started = True

    def _flush(self):
        """Завершить текущее слово, если оно было начато."""
        if self.started:
            self.tokens.append("".join(self.buffer))
        self.buffer = []
        self.started = False


def tokenize(line: str) -> list[str]:
    """Разбить строку на слова: первое - команда, остальные - аргументы.

    Кавычки ('...' и "...") объединяют слова с пробелами в один аргумент.
    Обратная косая черта экранирует следующий символ. Пустые кавычки ""
    дают пустой аргумент. Если кавычка не закрыта, бросается ParseError.
    """
    return Lexer(line).run()
