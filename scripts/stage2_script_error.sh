#!/bin/sh
# Этап 2: остановка скрипта на первой ошибке и неверный путь к скрипту.
cd "$(dirname "$0")/.." || exit 1
export PYTHONPATH=src

echo "== Скрипт с ошибкой: остановка на первой ошибке =="
python3 -m emulator --vfs ./vfs --prompt "err> " \
    --script examples/startup/stage2_error.txt

echo "== Несуществующий скрипт: ошибка параметров, код 2 =="
python3 -m emulator --vfs ./vfs --prompt "err> " \
    --script examples/startup/missing.txt
echo "Код завершения: $?"
