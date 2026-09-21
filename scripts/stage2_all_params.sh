#!/bin/sh
# Этап 2: все три параметра командной строки в одном запуске.
cd "$(dirname "$0")/.." || exit 1
export PYTHONPATH=src

python3 -m emulator \
    --vfs examples/vfs/several \
    --prompt "demo> " \
    --script examples/startup/stage2_demo.txt
echo "Код завершения: $?"
