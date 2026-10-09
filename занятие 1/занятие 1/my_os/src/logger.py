"""Модуль логирования системных вызовов."""
from src import db

def log_syscall(name, args="", user="system", status="OK"):
    """Записывает системный вызов в журнал syscalls_log."""
    db.execute_insert("syscalls_log", {
        "syscall_name": name,
        "args": str(args),
        "user": user,
        "status": status
    })