"""Тесты команд ls, cd и cat."""

from emulator.shell import Shell
from emulator.vfs import Vfs


def run(shell, line):
    """Выполнить строку и вернуть (успех, вывод)."""
    result = shell.execute(line)
    return result.ok, result.output


def test_ls_root_hides_dotfiles(tree_shell):
    """Команда ls без аргументов показывает текущую директорию без скрытых."""
    ok, out = run(tree_shell, "ls")
    assert ok
    assert out == "bin.dat  docs  empty  readme.txt  привет.txt"


def test_ls_all_shows_hidden(tree_shell):
    """Флаг -a показывает и скрытые файлы."""
    _, out = run(tree_shell, "ls -a")
    assert out.startswith(".hidden  bin.dat")


def test_ls_path(tree_shell):
    """Команда ls с путём показывает содержимое указанной директории."""
    _, out = run(tree_shell, "ls docs")
    assert out == "a.txt  b.txt  inner"


def test_ls_absolute_path(tree_shell):
    """Команда ls понимает абсолютные пути."""
    _, out = run(tree_shell, "ls /docs/inner")
    assert out == "deep.txt"


def test_ls_empty_directory(tree_shell):
    """Команда ls пустой директории ничего не печатает."""
    ok, out = run(tree_shell, "ls empty")
    assert ok
    assert out == ""


def test_ls_file_prints_its_name(tree_shell):
    """Команда ls файла печатает имя файла."""
    _, out = run(tree_shell, "ls readme.txt")
    assert out == "readme.txt"


def test_ls_several_paths_have_headers(tree_shell):
    """При нескольких путях перед каждой директорией печатается заголовок."""
    _, out = run(tree_shell, "ls docs empty")
    assert out == "docs:\na.txt  b.txt  inner\n\nempty:\n"


def test_ls_missing_path_is_error(tree_shell):
    """Команда ls несуществующего пути - ошибка в стиле UNIX."""
    ok, out = run(tree_shell, "ls nope")
    assert not ok
    assert out == "ls: cannot access 'nope': No such file or directory"


def test_ls_partial_failure_keeps_other_output(tree_shell):
    """Ошибка по одному пути не мешает вывести остальные."""
    ok, out = run(tree_shell, "ls docs nope")
    assert not ok
    assert "a.txt" in out
    assert "cannot access 'nope'" in out


def test_ls_through_file_is_error(tree_shell):
    """Путь через файл даёт ошибку Not a directory."""
    ok, out = run(tree_shell, "ls readme.txt/x")
    assert not ok
    assert out.endswith("Not a directory")


def test_ls_invalid_option(tree_shell):
    """Неизвестный флаг - ошибка."""
    ok, out = run(tree_shell, "ls -x")
    assert not ok
    assert out == "ls: invalid option -- 'x'"


def test_ls_quoted_name_with_spaces(tmp_path):
    """Имена с пробелами работают через кавычки."""
    root = tmp_path / "vfs"
    (root / "my dir").mkdir(parents=True)
    (root / "my dir" / "f.txt").write_text("f", encoding="utf-8")
    shell = Shell("a", "b", vfs=Vfs.from_directory(root))
    assert run(shell, 'ls "my dir"') == (True, "f.txt")


def test_cd_changes_directory_and_prompt(tree_shell):
    """Команда cd меняет директорию, приглашение показывает новый путь."""
    ok, out = run(tree_shell, "cd docs")
    assert ok
    assert out == ""
    assert tree_shell.prompt() == "alice@box:/docs$ "
    assert run(tree_shell, "ls")[1] == "a.txt  b.txt  inner"


def test_cd_relative_and_parent(tree_shell):
    """Относительные пути и .. работают."""
    run(tree_shell, "cd docs/inner")
    assert tree_shell.vfs.pwd() == "/docs/inner"
    run(tree_shell, "cd ../..")
    assert tree_shell.vfs.pwd() == "/"


def test_cd_without_arguments_goes_to_root(tree_shell):
    """Команда cd без аргументов возвращает в корень."""
    run(tree_shell, "cd docs")
    run(tree_shell, "cd")
    assert tree_shell.vfs.pwd() == "/"


def test_cd_above_root_stays_in_root(tree_shell):
    """Выше корня подняться нельзя."""
    run(tree_shell, "cd ../../..")
    assert tree_shell.vfs.pwd() == "/"


def test_cd_missing_directory(tree_shell):
    """Команда cd в несуществующую директорию - ошибка, cwd не меняется."""
    ok, out = run(tree_shell, "cd nope")
    assert not ok
    assert out == "cd: nope: No such file or directory"
    assert tree_shell.vfs.pwd() == "/"


def test_cd_into_file(tree_shell):
    """Команда cd в файл - ошибка Not a directory."""
    ok, out = run(tree_shell, "cd readme.txt")
    assert not ok
    assert out == "cd: readme.txt: Not a directory"


def test_cd_too_many_arguments(tree_shell):
    """Команда cd с двумя аргументами - ошибка."""
    ok, out = run(tree_shell, "cd docs empty")
    assert not ok
    assert out == "cd: too many arguments"


def test_cat_file(tree_shell):
    """Команда cat выводит содержимое файла."""
    assert run(tree_shell, "cat readme.txt") == (True, "root file\n")


def test_cat_several_files_are_concatenated(tree_shell):
    """Команда cat нескольких файлов склеивает их содержимое."""
    ok, out = run(tree_shell, "cat docs/a.txt docs/b.txt")
    assert ok
    assert out == "A text\nB text"


def test_cat_unicode_file(tree_shell):
    """Команда cat читает файлы в UTF-8 с русским текстом."""
    assert run(tree_shell, "cat привет.txt")[1] == "Привет\n"


def test_cat_binary_file_does_not_crash(tree_shell):
    """Недекодируемые байты заменяются, cat не падает."""
    ok, out = run(tree_shell, "cat bin.dat")
    assert ok
    assert "\ufffd" in out


def test_cat_relative_to_cwd(tree_shell):
    """Команда cat учитывает текущую директорию."""
    run(tree_shell, "cd docs")
    assert run(tree_shell, "cat a.txt")[1] == "A text\n"


def test_cat_missing_file(tree_shell):
    """Команда cat несуществующего файла - ошибка."""
    ok, out = run(tree_shell, "cat nope.txt")
    assert not ok
    assert out == "cat: nope.txt: No such file or directory\n"


def test_cat_directory(tree_shell):
    """Команда cat директории - ошибка Is a directory."""
    ok, out = run(tree_shell, "cat docs")
    assert not ok
    assert out == "cat: docs: Is a directory\n"


def test_cat_error_does_not_hide_other_files(tree_shell):
    """Ошибка одного файла не отменяет вывод остальных."""
    ok, out = run(tree_shell, "cat nope.txt readme.txt")
    assert not ok
    assert out.endswith("root file\n")


def test_cat_without_arguments(tree_shell):
    """Команда cat без аргументов - ошибка."""
    ok, out = run(tree_shell, "cat")
    assert not ok
    assert out == "cat: missing file operand"
