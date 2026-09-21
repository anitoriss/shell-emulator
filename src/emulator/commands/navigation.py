"""Команды навигации и чтения: ls, cd, cat."""

from emulator.result import CommandError, Result
from emulator.vfs import CURRENT, SEP, VfsError

ENCODING = "utf-8"
HIDDEN_PREFIX = "."
OPTION_PREFIX = "-"
ALL_FLAG = "-a"
NAME_SEPARATOR = "  "


def _parse_ls_args(args: list[str]) -> tuple[bool, list[str]]:
    """Разделить аргументы ls на флаг -a и список путей."""
    show_all = False
    paths = []
    for arg in args:
        if arg == ALL_FLAG:
            show_all = True
        elif arg.startswith(OPTION_PREFIX) and arg != OPTION_PREFIX:
            raise CommandError(f"ls: invalid option -- '{arg.lstrip('-')}'")
        else:
            paths.append(arg)
    return show_all, paths


def _list_one(vfs, path: str, show_all: bool, header: bool) -> str:
    """Вернуть вывод ls для одного пути (файл или директория)."""
    node = vfs.node_at(path)
    if not node.is_dir:
        return path
    names = sorted(node.children)
    if not show_all:
        names = [n for n in names if not n.startswith(HIDDEN_PREFIX)]
    text = NAME_SEPARATOR.join(names)
    return f"{path}:\n{text}" if header else text


def cmd_ls(shell, args: list[str]) -> Result:
    """Показать содержимое директорий (ls [-a] [путь...]).

    Без пути показывается текущая директория. Скрытые файлы (имя с точки)
    видны только с флагом -a. Для файла печатается его имя.
    """
    show_all, paths = _parse_ls_args(args)
    header = bool(paths[1:])
    blocks = []
    ok = True
    for path in paths or [CURRENT]:
        try:
            blocks.append(_list_one(shell.vfs, path, show_all, header))
        except VfsError as error:
            blocks.append(f"ls: cannot access '{path}': {error}")
            ok = False
    return Result("\n\n".join(blocks), ok)


def cmd_cd(shell, args: list[str]) -> Result:
    """Сменить текущую директорию (cd [путь]); без пути - корень."""
    if args[1:]:
        raise CommandError("cd: too many arguments")
    target = args[0] if args else SEP
    try:
        shell.vfs.change_dir(target)
    except VfsError as error:
        raise CommandError(f"cd: {target}: {error}") from error
    return Result()


def cmd_cat(shell, args: list[str]) -> Result:
    """Вывести содержимое файлов подряд (cat файл...)."""
    if not args:
        raise CommandError("cat: missing file operand")
    parts = []
    ok = True
    for path in args:
        try:
            data = shell.vfs.read_file(path)
        except VfsError as error:
            parts.append(f"cat: {path}: {error}\n")
            ok = False
        else:
            parts.append(data.decode(ENCODING, errors="replace"))
    return Result("".join(parts), ok)
