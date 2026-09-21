@echo off
rem Этап 3: разные варианты VFS (минимальный, несколько файлов, глубокий).
rem Статистика загруженной VFS печатается в консоль строкой [debug].
cd /d "%~dp0.."
set PYTHONPATH=src
set SCRIPT=examples\startup\exit_only.txt

echo == Минимальная VFS ==
python -m emulator --vfs examples\vfs\minimal --prompt "min> " --script %SCRIPT%

echo == Несколько файлов ==
python -m emulator --vfs examples\vfs\several --prompt "several> " --script %SCRIPT%

echo == Глубокая VFS (5 уровней) ==
python -m emulator --vfs examples\vfs\deep --prompt "deep> " --script %SCRIPT%

echo == Без --vfs: VFS по умолчанию ==
python -m emulator --script %SCRIPT%

echo == Несуществующая директория: ошибка, код 2 ==
python -m emulator --vfs examples\vfs\missing --script %SCRIPT%
echo Код завершения: %ERRORLEVEL%
