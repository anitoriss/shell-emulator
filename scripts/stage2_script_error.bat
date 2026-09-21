@echo off
rem Этап 2: остановка скрипта на первой ошибке и неверный путь к скрипту.
cd /d "%~dp0.."
set PYTHONPATH=src

echo == Скрипт с ошибкой: остановка на первой ошибке ==
python -m emulator --vfs examples\vfs\several --prompt "err> " --script examples\startup\stage2_error.txt

echo == Несуществующий скрипт: ошибка параметров, код 2 ==
python -m emulator --vfs examples\vfs\several --prompt "err> " --script examples\startup\missing.txt
echo Код завершения: %ERRORLEVEL%
