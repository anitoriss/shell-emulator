"""Общие фикстуры для тестов эмулятора."""

import pytest

from emulator.shell import Shell
from emulator.vfs import Vfs


def build_tree(root):
    """Создать на диске дерево для тестов команд и вернуть его корень."""
    (root / "docs" / "inner").mkdir(parents=True)
    (root / "empty").mkdir()
    (root / "readme.txt").write_text("root file\n", encoding="utf-8")
    (root / ".hidden").write_text("h\n", encoding="utf-8")
    (root / "привет.txt").write_text("Привет\n", encoding="utf-8")
    (root / "bin.dat").write_bytes(b"\xff\xfe")
    (root / "docs" / "a.txt").write_text("A text\n", encoding="utf-8")
    (root / "docs" / "b.txt").write_text("B text", encoding="utf-8")
    (root / "docs" / "inner" / "deep.txt").write_text(
        "deep\n", encoding="utf-8"
    )
    return root


@pytest.fixture
def tree_shell(tmp_path):
    """Вернуть оболочку с VFS, загруженной из тестового дерева."""
    root = build_tree(tmp_path / "vfs")
    return Shell("alice", "box", vfs=Vfs.from_directory(root))
