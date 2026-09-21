"""Реестр команд эмулятора: имя команды -> функция-обработчик."""

from emulator.commands.basic import cmd_cd, cmd_exit, cmd_ls

COMMANDS = {
    "cd": cmd_cd,
    "exit": cmd_exit,
    "ls": cmd_ls,
}
