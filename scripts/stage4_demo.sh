#!/bin/sh
# Этап 4: ls, cd, cat, uptime, who на разных VFS (диск не изменяется).
# После первого запуска (скрипт заканчивается ошибкой) закройте окно.
cd "$(dirname "$0")/.." || exit 1
export PYTHONPATH=src

echo "== deep: все команды, в конце ошибка =="
python3 -m emulator --vfs examples/vfs/deep --prompt "{user}:{cwd}> " \
    --script examples/startup/stage4_all.txt

echo "== several: скрытый файл и вложенная папка =="
python3 -m emulator --vfs examples/vfs/several --prompt "several:{cwd}> " \
    --script examples/startup/stage4_several.txt

echo "== minimal: интерактивный режим, введите команды вручную =="
python3 -m emulator --vfs examples/vfs/minimal
