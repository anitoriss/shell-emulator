"""Реестр команд эмулятора: имя команды -> функция-обработчик."""

from emulator.commands.basic import cmd_exit
from emulator.commands.info import cmd_uptime, cmd_who
from emulator.commands.modify import cmd_rmdir, cmd_touch
from emulator.commands.navigation import cmd_cat, cmd_cd, cmd_ls
from emulator.commands.system import cmd_vfs_init

COMMANDS = {
    "cat": cmd_cat,
    "cd": cmd_cd,
    "exit": cmd_exit,
    "ls": cmd_ls,
    "rmdir": cmd_rmdir,
    "touch": cmd_touch,
    "uptime": cmd_uptime,
    "vfs-init": cmd_vfs_init,
    "who": cmd_who,
}
