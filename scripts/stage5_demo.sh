#!/bin/sh
# Этап 5: touch и rmdir работают только в памяти, диск не меняется.
# Скрипты завершаются ошибкой намеренно - закройте окно вручную.
cd "$(dirname "$0")/.." || exit 1
export PYTHONPATH=src
work="$(mktemp -d)" || exit 1
cp -R examples/vfs/deep "$work/vfs"
mkdir "$work/vfs/empty_dir"

echo "== rmdir и touch на VFS с пустой директорией empty_dir =="
python3 -m emulator --vfs "$work/vfs" --prompt "{cwd}> " \
    --script examples/startup/stage5_vfs.txt

echo "Диск не изменился: empty_dir на месте, новых файлов нет:"
ls -A "$work/vfs"

echo "== VFS по умолчанию: все команды этапа 5, в конце ошибка =="
python3 -m emulator --prompt "{cwd}> " --script examples/startup/stage5_all.txt

echo "== Ошибка touch =="
python3 -m emulator --script examples/startup/stage5_errors.txt
rm -rf "$work"
