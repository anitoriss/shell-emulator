"""Виртуальная файловая система (VFS), целиком хранящаяся в памяти."""

from dataclasses import dataclass, field
from pathlib import Path

SEP = "/"
ROOT_NAME = ""

DEFAULT_TREE = {
    "home": {"user": {"welcome.txt": "Welcome to the emulator!\n"}},
    "etc": {"motd": "Have a nice day.\n"},
    "tmp": {},
}


class VfsError(Exception):
    """Ошибка загрузки или работы с VFS."""


@dataclass
class Node:
    """Узел VFS: файл (is_dir=False) или директория (is_dir=True)."""

    name: str
    is_dir: bool
    data: bytes = b""
    children: dict[str, "Node"] = field(default_factory=dict)


@dataclass(frozen=True)
class Stats:
    """Количество директорий и файлов в VFS (без корня)."""

    dirs: int = 0
    files: int = 0

    def __str__(self) -> str:
        """Вернуть краткое описание: «N dirs, M files»."""
        return f"{self.dirs} dirs, {self.files} files"


def _build_node(name: str, spec) -> Node:
    """Собрать узел из описания: строка - файл, словарь - директория."""
    if isinstance(spec, str):
        return Node(name, False, spec.encode("utf-8"))
    node = Node(name, True)
    for child_name, child_spec in spec.items():
        node.children[child_name] = _build_node(child_name, child_spec)
    return node


def _load_node(path: Path) -> Node:
    """Рекурсивно прочитать файл или директорию с диска в память."""
    if not path.is_dir():
        return Node(path.name, False, path.read_bytes())
    node = Node(path.name, True)
    for entry in sorted(path.iterdir()):
        if entry.is_symlink():
            continue
        if entry.is_dir() or entry.is_file():
            node.children[entry.name] = _load_node(entry)
    return node


def _count(node: Node) -> Stats:
    """Посчитать директории и файлы внутри узла node."""
    dirs = files = 0
    for child in node.children.values():
        if child.is_dir:
            inner = _count(child)
            dirs += 1 + inner.dirs
            files += inner.files
        else:
            files += 1
    return Stats(dirs, files)


class Vfs:
    """Дерево файлов и директорий в памяти и текущая директория."""

    def __init__(self, root: Node):
        """Создать VFS с корневой директорией root."""
        self.root = root
        self.cwd: list[Node] = []

    @classmethod
    def default(cls) -> "Vfs":
        """Создать VFS по умолчанию (встроенное небольшое дерево)."""
        return cls(_build_node(ROOT_NAME, DEFAULT_TREE))

    @classmethod
    def from_directory(cls, path: Path) -> "Vfs":
        """Загрузить в память содержимое директории path.

        Символические ссылки пропускаются. Файлы читаются как байты.
        """
        if not path.is_dir():
            raise VfsError(f"'{path}': not a directory")
        try:
            root = _load_node(path)
        except OSError as error:
            raise VfsError(f"cannot read '{path}': {error}") from error
        root.name = ROOT_NAME
        return cls(root)

    def stats(self) -> Stats:
        """Вернуть количество директорий и файлов."""
        return _count(self.root)

    def pwd(self) -> str:
        """Вернуть путь текущей директории, например /home/user."""
        return SEP + SEP.join(node.name for node in self.cwd)
