"""Тесты очистки физического представления VFS."""

from pathlib import Path

import pytest

from emulator.physical import clear_directory
from emulator.vfs import VfsError

REMOVED_TOP_LEVEL = 3


@pytest.fixture
def vfs_dir(tmp_path):
    """Создать директорию с файлами и вложенной папкой."""
    root = tmp_path / "vfs"
    (root / "sub" / "deeper").mkdir(parents=True)
    (root / "sub" / "deeper" / "f.txt").write_text("f", encoding="utf-8")
    (root / "one.txt").write_text("1", encoding="utf-8")
    (root / ".hidden").write_text("h", encoding="utf-8")
    return root


def test_clear_removes_everything_but_keeps_directory(vfs_dir):
    """Содержимое удаляется, сама директория остаётся."""
    removed = clear_directory(vfs_dir)
    assert removed == REMOVED_TOP_LEVEL
    assert vfs_dir.is_dir()
    assert list(vfs_dir.iterdir()) == []


def test_clear_refuses_current_directory(vfs_dir, monkeypatch):
    """Текущую директорию очищать нельзя."""
    monkeypatch.chdir(vfs_dir)
    with pytest.raises(VfsError):
        clear_directory(vfs_dir)
    assert (vfs_dir / "one.txt").exists()


def test_clear_refuses_parent_of_current_directory(vfs_dir, monkeypatch):
    """Родителя текущей директории очищать нельзя."""
    monkeypatch.chdir(vfs_dir / "sub")
    with pytest.raises(VfsError):
        clear_directory(vfs_dir)


def test_clear_refuses_git_repository(vfs_dir):
    """Директорию с .git очищать нельзя."""
    (vfs_dir / ".git").mkdir()
    with pytest.raises(VfsError):
        clear_directory(vfs_dir)
    assert (vfs_dir / "one.txt").exists()


def test_clear_refuses_home_directory(vfs_dir, monkeypatch):
    """Домашнюю директорию очищать нельзя."""
    monkeypatch.setattr(Path, "home", lambda: vfs_dir)
    with pytest.raises(VfsError):
        clear_directory(vfs_dir)


def test_clear_refuses_filesystem_root():
    """Корень файловой системы очищать нельзя."""
    with pytest.raises(VfsError):
        clear_directory(Path(Path.cwd().anchor))


def test_clear_missing_directory_is_error(tmp_path):
    """Несуществующую директорию очистить нельзя."""
    with pytest.raises(VfsError):
        clear_directory(tmp_path / "missing")
