"""Служебные команды эмулятора: vfs-init."""

from emulator.physical import clear_directory
from emulator.result import CommandError, Result
from emulator.vfs import Vfs, VfsError


def cmd_vfs_init(shell, args: list[str]) -> Result:
    """Заменить текущую VFS на VFS по умолчанию.

    Если VFS загружена из директории, физическое представление
    (содержимое этой директории на диске) очищается.
    """
    if args:
        raise CommandError("vfs-init: too many arguments")
    lines = []
    if shell.vfs_path is not None:
        try:
            removed = clear_directory(shell.vfs_path)
        except (VfsError, OSError) as error:
            raise CommandError(f"vfs-init: {error}") from error
        lines.append(f"cleared {shell.vfs_path} ({removed} entries removed)")
    shell.vfs = Vfs.default()
    lines.append("VFS reset to default")
    return Result("\n".join(lines))
