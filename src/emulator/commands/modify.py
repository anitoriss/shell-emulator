"""Команды, изменяющие VFS (только в памяти): touch и rmdir."""

from typing import Callable

from emulator.result import CommandError, Result
from emulator.vfs import VfsError


def _run_each(
    paths: list[str], action: Callable[[str], None], template: str
) -> Result:
    """Применить action к каждому пути, собирая сообщения об ошибках.

    template - шаблон сообщения с полями {path} и {reason}.
    """
    lines = []
    for path in paths:
        try:
            action(path)
        except VfsError as error:
            lines.append(template.format(path=path, reason=error))
    return Result("\n".join(lines), ok=not lines)


def cmd_touch(shell, args: list[str]) -> Result:
    """Создать пустые файлы (touch файл...), существующие не трогать."""
    if not args:
        raise CommandError("touch: missing file operand")
    message = "touch: cannot touch '{path}': {reason}"
    return _run_each(args, shell.vfs.touch, message)


def cmd_rmdir(shell, args: list[str]) -> Result:
    """Удалить пустые директории (rmdir директория...)."""
    if not args:
        raise CommandError("rmdir: missing operand")
    message = "rmdir: failed to remove '{path}': {reason}"
    return _run_each(args, shell.vfs.remove_dir, message)
