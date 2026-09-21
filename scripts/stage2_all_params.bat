@echo off
rem Этап 2: все три параметра командной строки в одном запуске.
cd /d "%~dp0.."
set PYTHONPATH=src

python -m emulator --vfs .\vfs --prompt "demo> " --script examples\startup\stage2_demo.txt
echo Код завершения: %ERRORLEVEL%
