#!/bin/sh
# Этап 3: разные варианты VFS (минимальный, несколько файлов, глубокий).
# Статистика загруженной VFS печатается в консоль строкой [debug].
cd "$(dirname "$0")/.." || exit 1
export PYTHONPATH=src
script=examples/startup/exit_only.txt

echo "== Минимальная VFS =="
python3 -m emulator --vfs examples/vfs/minimal --prompt "min> " --script $script

echo "== Несколько файлов =="
python3 -m emulator --vfs examples/vfs/several --prompt "several> " --script $script

echo "== Глубокая VFS (5 уровней) =="
python3 -m emulator --vfs examples/vfs/deep --prompt "deep> " --script $script

echo "== Без --vfs: VFS по умолчанию =="
python3 -m emulator --script $script

echo "== Несуществующая директория: ошибка, код 2 =="
python3 -m emulator --vfs examples/vfs/missing --script $script
echo "Код завершения: $?"
