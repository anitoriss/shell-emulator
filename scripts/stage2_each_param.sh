#!/bin/sh
# Этап 2: каждый параметр по отдельности.
# После запусков 1 и 3 закройте окно вручную (команда exit).
cd "$(dirname "$0")/.." || exit 1
export PYTHONPATH=src

echo "== 1. Только --prompt =="
python3 -m emulator --prompt "my-prompt> "

echo "== 2. Только --script =="
python3 -m emulator --script examples/startup/stage2_demo.txt

echo "== 3. Только --vfs =="
python3 -m emulator --vfs examples/vfs/several

echo "== 4. Все параметры вместе =="
python3 -m emulator --vfs examples/vfs/several --prompt "{user}> " \
    --script examples/startup/stage2_demo.txt
