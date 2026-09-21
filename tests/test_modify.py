"""Тесты команд touch и rmdir (изменения только в памяти)."""

from emulator.shell import Shell
from emulator.vfs import Vfs


def run(shell, line):
    """Выполнить строку и вернуть (успех, вывод)."""
    result = shell.execute(line)
    return result.ok, result.output


def test_touch_creates_empty_file(tree_shell):
    """Команда touch создаёт пустой файл в текущей директории."""
    assert run(tree_shell, "touch new.txt") == (True, "")
    assert "new.txt" in run(tree_shell, "ls")[1]
    assert run(tree_shell, "cat new.txt") == (True, "")


def test_touch_in_subdirectory_by_path(tree_shell):
    """Команда touch создаёт файл по относительному и абсолютному пути."""
    run(tree_shell, "touch docs/x.txt /empty/y.txt")
    assert "x.txt" in run(tree_shell, "ls docs")[1]
    assert run(tree_shell, "ls empty")[1] == "y.txt"


def test_touch_several_files(tree_shell):
    """Команда touch создаёт несколько файлов за раз."""
    run(tree_shell, "touch a b c")
    assert run(tree_shell, "ls")[1].startswith("a  b  bin.dat  c")


def test_touch_existing_file_keeps_content(tree_shell):
    """Команда touch не стирает содержимое существующего файла."""
    assert run(tree_shell, "touch readme.txt") == (True, "")
    assert run(tree_shell, "cat readme.txt")[1] == "root file\n"


def test_touch_existing_directory_is_ok(tree_shell):
    """Команда touch существующей директории не даёт ошибки."""
    assert run(tree_shell, "touch docs") == (True, "")


def test_touch_missing_parent_is_error(tree_shell):
    """Команда touch в несуществующей директории - ошибка."""
    ok, out = run(tree_shell, "touch nope/x.txt")
    assert not ok
    assert out == (
        "touch: cannot touch 'nope/x.txt': No such file or directory"
    )


def test_touch_parent_is_file(tree_shell):
    """Команда touch внутри файла - ошибка Not a directory."""
    ok, out = run(tree_shell, "touch readme.txt/x")
    assert not ok
    assert out.endswith("Not a directory")


def test_touch_trailing_slash_is_error(tree_shell):
    """Команда touch с косой чертой в конце нового имени - ошибка."""
    ok, _ = run(tree_shell, "touch newdir/")
    assert not ok


def test_touch_error_does_not_stop_other_files(tree_shell):
    """Ошибка по одному пути не мешает создать остальные файлы."""
    ok, out = run(tree_shell, "touch nope/x good.txt")
    assert not ok
    assert "nope/x" in out
    assert "good.txt" in run(tree_shell, "ls")[1]


def test_touch_without_arguments(tree_shell):
    """Команда touch без аргументов - ошибка."""
    ok, out = run(tree_shell, "touch")
    assert not ok
    assert out == "touch: missing file operand"


def test_rmdir_removes_empty_directory(tree_shell):
    """Команда rmdir удаляет пустую директорию."""
    assert run(tree_shell, "rmdir empty") == (True, "")
    assert "empty" not in run(tree_shell, "ls")[1]


def test_rmdir_trailing_slash_and_absolute_path(tree_shell):
    """Команда rmdir понимает косую черту в конце и абсолютный путь."""
    assert run(tree_shell, "rmdir /empty/")[0]
    assert "empty" not in run(tree_shell, "ls")[1]


def test_rmdir_not_empty(tree_shell):
    """Команда rmdir непустой директории - ошибка, директория остаётся."""
    ok, out = run(tree_shell, "rmdir docs")
    assert not ok
    assert out == "rmdir: failed to remove 'docs': Directory not empty"
    assert "docs" in run(tree_shell, "ls")[1]


def test_rmdir_file_is_error(tree_shell):
    """Команда rmdir файла - ошибка Not a directory."""
    ok, out = run(tree_shell, "rmdir readme.txt")
    assert not ok
    assert out.endswith("Not a directory")


def test_rmdir_missing_is_error(tree_shell):
    """Команда rmdir несуществующей директории - ошибка."""
    ok, out = run(tree_shell, "rmdir nope")
    assert not ok
    assert out.endswith("No such file or directory")


def test_rmdir_root_is_invalid(tree_shell):
    """Корень удалить нельзя."""
    ok, out = run(tree_shell, "rmdir /")
    assert not ok
    assert out.endswith("Invalid argument")


def test_rmdir_current_directory_is_invalid(tree_shell):
    """Текущую директорию удалить нельзя ни по имени, ни через точку."""
    run(tree_shell, "cd empty")
    assert not run(tree_shell, "rmdir .")[0]
    assert not run(tree_shell, "rmdir /empty")[0]
    assert not run(tree_shell, "rmdir ../empty")[0]
    assert tree_shell.vfs.pwd() == "/empty"


def test_rmdir_dot_suffix_is_invalid(tree_shell):
    """Путь, оканчивающийся на . или .., удалить нельзя."""
    assert not run(tree_shell, "rmdir empty/.")[0]
    assert not run(tree_shell, "rmdir empty/..")[0]
    assert "empty" in run(tree_shell, "ls")[1]


def test_rmdir_after_touch_becomes_impossible(tree_shell):
    """Пустую директорию, куда добавили файл, удалить уже нельзя."""
    run(tree_shell, "touch empty/f")
    ok, out = run(tree_shell, "rmdir empty")
    assert not ok
    assert out.endswith("Directory not empty")


def test_rmdir_error_does_not_stop_other_directories(tree_shell):
    """Ошибка по одному пути не мешает удалить остальные директории."""
    ok, _ = run(tree_shell, "rmdir docs empty")
    assert not ok
    assert "empty" not in run(tree_shell, "ls")[1]


def test_rmdir_without_arguments(tree_shell):
    """Команда rmdir без аргументов - ошибка."""
    ok, out = run(tree_shell, "rmdir")
    assert not ok
    assert out == "rmdir: missing operand"


def test_changes_stay_in_memory(tmp_path):
    """Команды touch и rmdir не меняют файлы на диске."""
    root = tmp_path / "vfs"
    (root / "empty").mkdir(parents=True)
    (root / "file.txt").write_text("x", encoding="utf-8")
    before = sorted(str(p) for p in root.rglob("*"))
    shell = Shell("a", "b", vfs=Vfs.from_directory(root))
    run(shell, "touch created.txt")
    run(shell, "rmdir empty")
    assert sorted(str(p) for p in root.rglob("*")) == before
