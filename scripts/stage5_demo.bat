@echo off
rem Этап 5: touch и rmdir работают только в памяти, диск не меняется.
rem Скрипты завершаются ошибкой намеренно - закройте окно вручную.
cd /d "%~dp0.."
set PYTHONPATH=src
set WORK=%TEMP%\emulator_vfs_demo
if exist "%WORK%" rmdir /S /Q "%WORK%"
xcopy examples\vfs\deep "%WORK%\vfs" /E /I /Q >nul
mkdir "%WORK%\vfs\empty_dir"

echo == rmdir и touch на VFS с пустой директорией empty_dir ==
python -m emulator --vfs "%WORK%\vfs" --prompt "{cwd}> " --script examples\startup\stage5_vfs.txt

echo Диск не изменился: empty_dir на месте, новых файлов нет:
dir /B "%WORK%\vfs"

echo == VFS по умолчанию: все команды этапа 5, в конце ошибка ==
python -m emulator --prompt "{cwd}> " --script examples\startup\stage5_all.txt

echo == Ошибка touch ==
python -m emulator --script examples\startup\stage5_errors.txt
rmdir /S /Q "%WORK%"
