"""Тесты разбора командной строки (парсера с кавычками)."""

import pytest

from emulator.parser import ParseError, tokenize


def test_plain_words():
    """Слова без кавычек разделяются пробелами."""
    assert tokenize("ls -l /tmp") == ["ls", "-l", "/tmp"]


def test_extra_whitespace_is_ignored():
    """Лишние пробелы и табуляции между словами не создают аргументов."""
    assert tokenize("  ls \t  -l  ") == ["ls", "-l"]


def test_empty_line_gives_no_tokens():
    """Пустая строка и строка из пробелов дают пустой список."""
    assert tokenize("") == []
    assert tokenize("   ") == []


def test_double_quotes_join_words():
    """Двойные кавычки объединяют слова в один аргумент."""
    assert tokenize('ls "my documents"') == ["ls", "my documents"]


def test_single_quotes_join_words():
    """Одинарные кавычки объединяют слова в один аргумент."""
    assert tokenize("cd 'my folder'") == ["cd", "my folder"]


def test_quotes_inside_other_quotes_are_literal():
    """Кавычки другого вида внутри кавычек остаются обычными символами."""
    assert tokenize("""echo "it's" 'say "hi"'""") == [
        "echo", "it's", 'say "hi"',
    ]


def test_adjacent_quoted_parts_are_glued():
    """Части слова, записанные рядом, склеиваются в один аргумент."""
    assert tokenize('echo a"b c"d') == ["echo", "ab cd"]


def test_empty_quotes_give_empty_argument():
    """Пустые кавычки создают пустой аргумент."""
    assert tokenize('cat ""') == ["cat", ""]


def test_backslash_escapes_space():
    """Обратная косая черта экранирует пробел вне кавычек."""
    assert tokenize(r"ls my\ dir") == ["ls", "my dir"]


def test_escaped_quote_inside_double_quotes():
    """Внутри двойных кавычек можно экранировать кавычку."""
    assert tokenize(r'echo "a\"b"') == ["echo", 'a"b']


def test_backslash_is_literal_in_single_quotes():
    """Внутри одинарных кавычек обратная косая черта не экранирует."""
    assert tokenize(r"echo 'a\b'") == ["echo", "a\\b"]


def test_unknown_escape_in_double_quotes_keeps_backslash():
    """Неизвестное экранирование в двойных кавычках остаётся как есть."""
    assert tokenize(r'echo "a\qb"') == ["echo", "a\\qb"]


def test_unterminated_quote_is_error():
    """Незакрытая кавычка приводит к ParseError."""
    with pytest.raises(ParseError):
        tokenize('ls "oops')


def test_trailing_backslash_is_error():
    """Строка, оканчивающаяся обратной косой чертой, - ошибка."""
    with pytest.raises(ParseError):
        tokenize("ls oops\\")
