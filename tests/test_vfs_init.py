"""Тесты команды vfs-init."""

import pytest

from emulator.shell import Shell
from emulator.vfs import Vfs


@pytest.fixture
def disk_vfs(tmp_path):
    """Вернуть (директорию VFS на диске, оболочку с этой VFS)."""
    root = tmp_path / "vfs"
    (root / "dir").mkdir(parents=True)
    (root / "custom.txt").write_text("custom", encoding="utf-8")
    shell = Shell("alice", "box", vfs=Vfs.from_directory(root), vfs_path=root)
    return root, shell


def test_vfs_init_replaces_memory_and_clears_disk(disk_vfs):
    """vfs-init подменяет VFS в памяти и очищает директорию на диске."""
    root, shell = disk_vfs
    result = shell.execute("vfs-init")
    assert result.ok
    assert "custom.txt" not in shell.vfs.root.children
    assert "home" in shell.vfs.root.children
    assert list(root.iterdir()) == []


def test_vfs_init_without_disk_path_changes_memory_only():
    """Без физического пути vfs-init только сбрасывает VFS в памяти."""
    shell = Shell("alice", "box")
    shell.vfs.root.children.clear()
    result = shell.execute("vfs-init")
    assert result.ok
    assert "home" in shell.vfs.root.children


def test_vfs_init_rejects_arguments(disk_vfs):
    """Лишние аргументы - ошибка, диск и память не меняются."""
    root, shell = disk_vfs
    result = shell.execute("vfs-init now")
    assert not result.ok
    assert (root / "custom.txt").exists()
    assert "custom.txt" in shell.vfs.root.children


def test_vfs_init_refusal_keeps_memory_vfs(disk_vfs, monkeypatch):
    """Если очистка запрещена, VFS в памяти остаётся прежней."""
    root, shell = disk_vfs
    monkeypatch.chdir(root)
    result = shell.execute("vfs-init")
    assert not result.ok
    assert result.output.startswith("vfs-init: refusing")
    assert "custom.txt" in shell.vfs.root.children
    assert (root / "custom.txt").exists()
