"""Реестр команд эмулятора: имя команды -> функция-обработчик."""

from emulator.commands.basic import cmd_cd, cmd_exit, cmd_ls
from emulator.commands.system import cmd_vfs_init

COMMANDS = {
    "cd": cmd_cd,
    "exit": cmd_exit,
    "ls": cmd_ls,
    "vfs-init": cmd_vfs_init,
}
