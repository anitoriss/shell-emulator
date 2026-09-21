@echo off
rem Этап 4: ls, cd, cat, uptime, who на разных VFS (диск не изменяется).
rem После первого запуска (скрипт заканчивается ошибкой) закройте окно.
cd /d "%~dp0.."
set PYTHONPATH=src

echo == deep: все команды, в конце ошибка ==
python -m emulator --vfs examples\vfs\deep --prompt "{user}:{cwd}> " --script examples\startup\stage4_all.txt

echo == several: скрытый файл и вложенная папка ==
python -m emulator --vfs examples\vfs\several --prompt "several:{cwd}> " --script examples\startup\stage4_several.txt

echo == minimal: интерактивный режим, введите команды вручную ==
python -m emulator --vfs examples\vfs\minimal
