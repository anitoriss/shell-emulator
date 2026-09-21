"""Тесты виртуальной файловой системы (загрузка в память)."""

import os
from pathlib import Path

import pytest

from emulator.vfs import Stats, Vfs, VfsError

DEEP = Path(__file__).parent.parent / "examples" / "vfs" / "deep"
DEEP_DIRS = 6
DEEP_FILES = 5
DEFAULT_DIRS = 4
DEFAULT_FILES = 2


def make_tree(base):
    """Создать на диске небольшое дерево и вернуть его корень."""
    root = base / "vfs"
    (root / "a" / "b").mkdir(parents=True)
    (root / "empty").mkdir()
    (root / "top.txt").write_text("top\n", encoding="utf-8")
    (root / "a" / "b" / "deep.txt").write_bytes(b"\x00\x01binary")
    return root


def test_default_vfs_has_builtin_tree():
    """VFS по умолчанию содержит встроенное дерево, в т. ч. пустую tmp."""
    vfs = Vfs.default()
    assert sorted(vfs.root.children) == ["etc", "home", "tmp"]
    assert vfs.root.children["tmp"].children == {}
    assert vfs.stats() == Stats(DEFAULT_DIRS, DEFAULT_FILES)


def test_from_directory_loads_nested_tree(tmp_path):
    """Вложенные директории и файлы загружаются в память."""
    vfs = Vfs.from_directory(make_tree(tmp_path))
    nested = vfs.root.children["a"].children["b"].children["deep.txt"]
    assert not nested.is_dir
    assert nested.data == b"\x00\x01binary"
    assert vfs.root.children["empty"].is_dir


def test_root_has_empty_name(tmp_path):
    """Корень VFS не хранит имя реальной директории."""
    vfs = Vfs.from_directory(make_tree(tmp_path))
    assert vfs.root.name == ""


def test_stats_counts_dirs_and_files(tmp_path):
    """Статистика считает директории и файлы (без корня)."""
    vfs = Vfs.from_directory(make_tree(tmp_path))
    assert vfs.stats() == Stats(dirs=3, files=2)
    assert str(vfs.stats()) == "3 dirs, 2 files"


def test_sample_deep_vfs_has_three_levels():
    """Пример deep содержит не менее трёх уровней вложенности."""
    vfs = Vfs.from_directory(DEEP)
    assert vfs.stats() == Stats(DEEP_DIRS, DEEP_FILES)
    docs = vfs.root.children["home"].children["user"].children["docs"]
    report = docs.children["report.txt"].data.decode("utf-8")
    assert report.startswith("Отчёт")


def test_not_a_directory_is_error(tmp_path):
    """Путь к файлу или несуществующий путь - ошибка VfsError."""
    file_path = tmp_path / "file.txt"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(VfsError):
        Vfs.from_directory(file_path)
    with pytest.raises(VfsError):
        Vfs.from_directory(tmp_path / "missing")


def test_symlinks_are_skipped(tmp_path):
    """Символические ссылки не загружаются (нет зацикливания)."""
    root = make_tree(tmp_path)
    try:
        os.symlink(root, root / "loop", target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("символические ссылки недоступны")
    vfs = Vfs.from_directory(root)
    assert "loop" not in vfs.root.children


def test_load_does_not_modify_disk(tmp_path):
    """Загрузка VFS ничего не меняет на диске."""
    root = make_tree(tmp_path)
    before = sorted(str(p) for p in root.rglob("*"))
    Vfs.from_directory(root)
    assert sorted(str(p) for p in root.rglob("*")) == before


def test_pwd_of_new_vfs_is_root(tmp_path):
    """Сразу после загрузки текущая директория - корень."""
    assert Vfs.from_directory(make_tree(tmp_path)).pwd() == "/"
