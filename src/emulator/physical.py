"""Операции с физическим представлением VFS на диске."""

import shutil
from pathlib import Path

from emulator.vfs import VfsError

GIT_MARKER = ".git"


def ensure_safe_to_clear(path: Path) -> None:
    """Запретить очистку опасных директорий.

    Нельзя очищать корень диска, домашнюю директорию, текущую директорию
    (и её родителей), а также директорию, в которой лежит .git.
    """
    resolved = path.resolve()
    cwd = Path.cwd().resolve()
    if resolved == resolved.parent:
        raise VfsError("refusing to clear the filesystem root")
    if resolved == Path.home().resolve():
        raise VfsError("refusing to clear the home directory")
    if resolved == cwd or resolved in cwd.parents:
        raise VfsError("refusing to clear the current directory or its parent")
    if (resolved / GIT_MARKER).exists():
        raise VfsError("refusing to clear a git repository")


def clear_directory(path: Path) -> int:
    """Удалить всё содержимое директории path, оставив саму директорию.

    Возвращает число удалённых элементов верхнего уровня.
    """
    if not path.is_dir():
        raise VfsError(f"'{path}': not a directory")
    ensure_safe_to_clear(path)
    removed = 0
    for entry in path.iterdir():
        if entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry)
        else:
            entry.unlink()
        removed += 1
    return removed
