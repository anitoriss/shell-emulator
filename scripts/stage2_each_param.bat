@echo off
rem Этап 2: каждый параметр по отдельности.
rem После запусков 1 и 3 закройте окно вручную (команда exit).
cd /d "%~dp0.."
set PYTHONPATH=src

echo == 1. Только --prompt ==
python -m emulator --prompt "my-prompt> "

echo == 2. Только --script ==
python -m emulator --script examples\startup\stage2_demo.txt

echo == 3. Только --vfs ==
python -m emulator --vfs examples\vfs\several

echo == 4. Все параметры вместе ==
python -m emulator --vfs examples\vfs\several --prompt "{user}> " --script examples\startup\stage2_demo.txt
