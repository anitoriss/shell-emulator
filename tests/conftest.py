"""Общие фикстуры для тестов эмулятора."""

import pytest

from emulator.shell import Shell
from emulator.vfs import Vfs


def _write(path, text):
    """Записать текстовый файл без перевода строк в CRLF на Windows.

    Без newline="" Windows превращает конец строки в тексте в
    два символа вместо одного, и тесты перестают совпадать с ожиданием.
    """
    path.write_text(text, encoding="utf-8", newline="")


def build_tree(root):
    """Создать на диске дерево для тестов команд и вернуть его корень."""
    (root / "docs" / "inner").mkdir(parents=True)
    (root / "empty").mkdir()
    _write(root / "readme.txt", "root file\n")
    _write(root / ".hidden", "h\n")
    _write(root / "привет.txt", "Привет\n")
    (root / "bin.dat").write_bytes(b"\xff\xfe")
    _write(root / "docs" / "a.txt", "A text\n")
    _write(root / "docs" / "b.txt", "B text")
    _write(root / "docs" / "inner" / "deep.txt", "deep\n")
    return root


@pytest.fixture
def tree_shell(tmp_path):
    """Вернуть оболочку с VFS, загруженной из тестового дерева."""
    root = build_tree(tmp_path / "vfs")
    return Shell("alice", "box", vfs=Vfs.from_directory(root))
