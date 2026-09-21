"""Виртуальная файловая система (VFS), целиком хранящаяся в памяти."""

import posixpath
from dataclasses import dataclass, field
from pathlib import Path

SEP = "/"
CURRENT = "."
PARENT = ".."
ROOT_NAME = ""
SKIPPED_PARTS = ("", CURRENT)

DEFAULT_TREE = {
    "home": {"user": {"welcome.txt": "Welcome to the emulator!\n"}},
    "etc": {"motd": "Have a nice day.\n"},
    "tmp": {},
}


class VfsError(Exception):
    """Ошибка VFS; текст по умолчанию хранится в атрибуте message."""

    message = "Input/output error"

    def __init__(self, message: str | None = None):
        """Создать ошибку с собственным текстом или текстом по умолчанию."""
        super().__init__(message or self.message)


class NoEntryError(VfsError):
    """Путь не существует."""

    message = "No such file or directory"


class NotDirError(VfsError):
    """Ожидалась директория, но найден файл."""

    message = "Not a directory"


class IsDirError(VfsError):
    """Ожидался файл, но найдена директория."""

    message = "Is a directory"


class NotEmptyError(VfsError):
    """Директория не пуста."""

    message = "Directory not empty"


class InvalidError(VfsError):
    """Недопустимый аргумент (корень, ., .., текущая директория)."""

    message = "Invalid argument"


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

    def walk(self, path: str) -> list[Node]:
        """Пройти по пути и вернуть цепочку узлов от корня (без корня).

        Абсолютный путь начинается с /, иначе отсчёт идёт от текущей
        директории. Понимает . и .. . Пустой путь - ошибка NoEntryError.
        """
        if not path:
            raise NoEntryError()
        chain = [] if path.startswith(SEP) else list(self.cwd)
        for part in path.split(SEP):
            if part not in SKIPPED_PARTS:
                self._step(chain, part)
        return chain

    def node_at(self, path: str) -> Node:
        """Найти узел по пути (корень, если цепочка пуста)."""
        return self._tail(self.walk(path))

    def change_dir(self, path: str) -> None:
        """Сделать директорию path текущей."""
        chain = self.walk(path)
        if not self._tail(chain).is_dir:
            raise NotDirError()
        self.cwd = chain

    def read_file(self, path: str) -> bytes:
        """Вернуть содержимое файла path."""
        node = self.node_at(path)
        if node.is_dir:
            raise IsDirError()
        return node.data

    def touch(self, path: str) -> None:
        """Создать пустой файл path, если его ещё нет.

        Если путь уже существует, ничего не происходит (времена
        изменения в VFS не хранятся).
        """
        try:
            self.walk(path)
        except NoEntryError:
            self._create_file(path)

    def remove_dir(self, path: str) -> None:
        """Удалить пустую директорию path (аналог rmdir).

        Нельзя удалить корень, текущую директорию (и её родителей),
        а также путь, оканчивающийся на . или .. .
        """
        if posixpath.basename(path.rstrip(SEP)) in (CURRENT, PARENT):
            raise InvalidError()
        chain = self.walk(path)
        if not chain:
            raise InvalidError()
        target = chain[-1]
        if not target.is_dir:
            raise NotDirError()
        if target.children:
            raise NotEmptyError()
        if any(node is target for node in self.cwd):
            raise InvalidError()
        del self._tail(chain[:-1]).children[target.name]

    def _create_file(self, path: str) -> None:
        """Создать пустой файл в существующей родительской директории."""
        if path.endswith(SEP):
            raise NoEntryError()
        parent_path, name = posixpath.split(path)
        parent = self.node_at(parent_path or CURRENT)
        if not parent.is_dir:
            raise NotDirError()
        parent.children[name] = Node(name, False)

    def _tail(self, chain: list[Node]) -> Node:
        """Вернуть последний узел цепочки или корень, если она пуста."""
        return chain[-1] if chain else self.root

    def _step(self, chain: list[Node], part: str) -> None:
        """Сделать шаг пути: в дочерний узел или на уровень вверх."""
        here = self._tail(chain)
        if not here.is_dir:
            raise NotDirError()
        if part == PARENT:
            if chain:
                chain.pop()
            return
        child = here.children.get(part)
        if child is None:
            raise NoEntryError()
        chain.append(child)
