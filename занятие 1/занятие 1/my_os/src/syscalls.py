"""Слой системных вызовов (API Ядра)."""
from src.logger import log_syscall
from src.auth import authenticate, check_permission
from src.kernel import kernel_instance
from src import fs, scheduler


def sys_login(login, password, current_user="guest"):
    log_syscall("sys_login", login, current_user, "check")
    user = authenticate(login, password)
    if user:
        kernel_instance.set_user(login)
        log_syscall("sys_login", login, current_user, "OK")
        return True
    log_syscall("sys_login", login, current_user, "DENIED")
    return False


def sys_logout(current_user="guest"):
    log_syscall("sys_logout", "", current_user, "OK")
    kernel_instance.set_user("guest")
    return True


def sys_whoami(current_user="guest"):
    log_syscall("sys_whoami", "", current_user, "OK")
    return kernel_instance.get_user()


def sys_create_file(path, content, current_user="guest"):
    log_syscall("sys_create_file", path, current_user, "check")
    fid = fs.create_file(path, content, current_user)
    if fid == -1:
        log_syscall("sys_create_file", path, current_user, "EXISTS")
        return -1
    log_syscall("sys_create_file", path, current_user, "OK")
    return fid


def sys_read_file(path, current_user="guest"):
    log_syscall("sys_read_file", path, current_user, "check")
    content = fs.read_file(path)
    log_syscall("sys_read_file", path, current_user, "OK")
    return content


def sys_delete_file(path, current_user="guest", owner=None):
    log_syscall("sys_delete_file", path, current_user, "check")
    if owner is None:
        owner = fs.get_owner(path)
    if owner is None:
        log_syscall("sys_delete_file", path, current_user, "NOT_FOUND")
        return False
    if not check_permission(current_user, "delete_file", owner):
        log_syscall("sys_delete_file", path, current_user, "DENIED")
        return False
    fs.delete_file(path)
    log_syscall("sys_delete_file", path, current_user, "OK")
    return True


def sys_list_files(prefix="", current_user="guest"):
    log_syscall("sys_list_files", prefix, current_user, "OK")
    return fs.list_files(prefix)


def sys_exec(name, current_user="guest"):
    log_syscall("sys_exec", name, current_user, "check")
    pid = scheduler.create_process(name, current_user)
    if pid == -1:
        log_syscall("sys_exec", name, current_user, "NO_MEMORY")
        return -1
    log_syscall("sys_exec", name, current_user, "OK")
    return pid


def sys_ps(current_user="guest"):
    log_syscall("sys_ps", "", current_user, "OK")
    return scheduler.list_processes()


def sys_kill(pid, current_user="guest"):
    log_syscall("sys_kill", str(pid), current_user, "check")
    proc = scheduler.get_process(pid)
    owner = proc["owner"] if proc else None
    if not check_permission(current_user, "kill", owner):
        log_syscall("sys_kill", str(pid), current_user, "DENIED")
        return False
    res = scheduler.terminate_process(pid)
    status = "OK" if res else "NOT_FOUND"
    log_syscall("sys_kill", str(pid), current_user, status)
    return res


def sys_mem_alloc(size, current_user="guest"):
    log_syscall("sys_mem_alloc", str(size), current_user, "check")
    res = kernel_instance.allocate_memory(size)
    log_syscall("sys_mem_alloc", str(size), current_user, "OK" if res else "NO_MEMORY")
    return res


def sys_logs(limit=10, current_user="guest"):
    from src import db

    log_syscall("sys_logs", str(limit), current_user, "OK")
    logs = db.execute_select("syscalls_log")
    return logs[-limit:]


def sys_shutdown(current_user="guest"):
    log_syscall("sys_shutdown", "", current_user, "OK")
    return True