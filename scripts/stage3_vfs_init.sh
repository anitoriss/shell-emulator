#!/bin/sh
# Этап 3: vfs-init на КОПИИ VFS (команда очищает директорию на диске).
# Во втором запуске (скрипт с ошибкой) закройте окно вручную.
cd "$(dirname "$0")/.." || exit 1
export PYTHONPATH=src
work="$(mktemp -d)" || exit 1
cp -R examples/vfs/deep "$work/vfs"

echo "== Скрипт с ошибкой: диск не затрагивается =="
python3 -m emulator --vfs "$work/vfs" --script examples/startup/stage3_errors.txt
echo "Элементов в копии VFS после ошибки (ожидается 11):"
find "$work/vfs" -mindepth 1 | wc -l

echo "== Скрипт со всеми командами, включая vfs-init =="
python3 -m emulator --vfs "$work/vfs" --prompt "vfs> " \
    --script examples/startup/stage3_all.txt
echo "Элементов в копии VFS после vfs-init (ожидается 0):"
find "$work/vfs" -mindepth 1 | wc -l
rm -rf "$work"
