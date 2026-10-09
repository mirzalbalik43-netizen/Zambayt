"""Планировщик процессов."""
from src import db
from src.kernel import kernel_instance

def create_process(name, owner, memory_size=10):
    """Создание и запуск процесса."""
    if not kernel_instance.allocate_memory(memory_size):
        return -1
    pid = kernel_instance.allocate_pid()
    db.execute_insert("processes", {
        "pid": pid,
        "name": name,
        "state": "ready",
        "owner": owner,
        "memory_used": memory_size
    })
    return pid

def list_processes():
    """Возвращает список всех процессов."""
    return db.execute_select("processes")

def get_process(pid):
    """Получение процесса по PID."""
    procs = db.execute_select("processes", {"pid": pid})
    return procs[0] if procs else None

def terminate_process(pid):
    """Завершение процесса и освобождение памяти."""
    proc = get_process(pid)
    if not proc:
        return False
    kernel_instance.free_memory(proc["memory_used"])
    db.execute_delete("processes", {"pid": pid})
    return True

def schedule_round_robin():
    """Алгоритм планирования Round-Robin."""
    procs = list_processes()
    if not procs:
        return None
    for p in procs:
        db.execute_update("processes", {"state": "ready"}, {"pid": p["pid"]})
    first_pid = procs[0]["pid"]
    db.execute_update("processes", {"state": "running"}, {"pid": first_pid})
    return get_process(first_pid)