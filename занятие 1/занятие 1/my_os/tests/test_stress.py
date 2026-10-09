"""Стресс-тесты системы."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import db
from src.kernel import kernel_instance
from src.syscalls import sys_exec, sys_kill, sys_create_file, sys_delete_file, sys_login
from src.auth import register_user


def setup():
    db.execute_delete("users", {"login": "stress_admin"})
    register_user("stress_admin", "stress123", "admin")
    procs = db.execute_select("processes")
    for p in procs:
        try:
            kernel_instance.free_memory(p["memory_used"])
        except Exception:
            pass
        db.execute_delete("processes", {"pid": p["pid"]})


def test_many_processes():
    """Создать 10 процессов и проверить, что система выдерживает."""
    sys_login("stress_admin", "stress123")
    pids = []
    for i in range(10):
        pid = sys_exec(f"stress_{i}", "stress_admin")
        assert pid > 0, f"Процесс {i} не создан"
        pids.append(pid)
    print(f"[PASS] создано 10 процессов: {pids}")

    procs = db.execute_select("processes")
    assert len(procs) == 10
    print("[PASS] в таблице 10 процессов")

    for pid in pids:
        sys_kill(pid, "stress_admin")
    procs_after = db.execute_select("processes")
    assert len(procs_after) == 0
    print("[PASS] все процессы завершены")


def test_memory_limit_stress():
    """Проверить, что лимит памяти соблюдается."""
    sys_login("stress_admin", "stress123")
    pids = []
    for i in range(100):
        pid = sys_exec(f"mem_{i}", "stress_admin", 100)
        if pid == -1:
            break
        pids.append(pid)
    assert len(pids) < 100, "Лимит памяти не соблюдается"
    print(f"[PASS] лимит памяти соблюдается, создано {len(pids)} процессов")
    for pid in pids:
        sys_kill(pid, "stress_admin")


def test_many_files():
    """Создать 50 файлов и проверить систему."""
    sys_login("stress_admin", "stress123")
    fids = []
    for i in range(50):
        fid = sys_create_file(f"/stress_{i}.txt", f"content_{i}", "stress_admin")
        assert fid > 0, f"Файл {i} не создан"
        fids.append(fid)
    print(f"[PASS] создано 50 файлов")

    files = db.execute_select("files")
    stress_files = [f for f in files if f["path"].startswith("/stress_")]
    assert len(stress_files) == 50
    print("[PASS] в таблице 50 файлов")

    for i in range(50):
        sys_delete_file(f"/stress_{i}.txt", "stress_admin")
    print("[PASS] все файлы удалены")


def test_many_users():
    """Создать 20 пользователей и проверить систему."""
    for i in range(20):
        db.execute_delete("users", {"login": f"bulk_{i}"})
        register_user(f"bulk_{i}", f"pass{i}123", "user")
    users = db.execute_select("users")
    bulk_users = [u for u in users if u["login"].startswith("bulk_")]
    assert len(bulk_users) == 20
    print("[PASS] создано 20 пользователей")


if __name__ == "__main__":
    setup()
    test_many_processes()
    test_memory_limit_stress()
    test_many_files()
    test_many_users()
    print("\nВсе стресс-тесты пройдены.")