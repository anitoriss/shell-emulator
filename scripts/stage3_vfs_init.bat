@echo off
rem Этап 3: vfs-init на КОПИИ VFS (команда очищает директорию на диске).
rem В первом запуске (скрипт с ошибкой) закройте окно вручную.
cd /d "%~dp0.."
set PYTHONPATH=src
set WORK=%TEMP%\emulator_vfs_demo
if exist "%WORK%" rmdir /S /Q "%WORK%"
xcopy examples\vfs\deep "%WORK%\vfs" /E /I /Q >nul

echo == Скрипт с ошибкой: диск не затрагивается ==
python -m emulator --vfs "%WORK%\vfs" --script examples\startup\stage3_errors.txt
echo Содержимое копии VFS после ошибки (файлы на месте):
dir /B "%WORK%\vfs"

echo == Скрипт со всеми командами, включая vfs-init ==
python -m emulator --vfs "%WORK%\vfs" --prompt "vfs> " --script examples\startup\stage3_all.txt
echo Содержимое копии VFS после vfs-init (ожидается пусто):
dir /B "%WORK%\vfs"
rmdir /S /Q "%WORK%"
