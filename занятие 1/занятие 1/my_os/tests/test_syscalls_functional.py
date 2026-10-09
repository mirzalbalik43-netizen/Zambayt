"""Функциональные тесты системных вызовов (11 тестов)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import db
from src.auth import register_user
from src.syscalls import (
    sys_login, sys_create_file, sys_read_file, sys_delete_file,
    sys_exec, sys_kill,
)


def setup():
    db.init_db()
    db.execute_delete("files", {})
    db.execute_delete("users", {})
    db.execute_delete("syscalls_log", {})
    db.execute_delete("processes", {})
    register_user("admin", "admin1234", "admin")


def run():
    passed = 0
    total = 0

    def check(name, cond):
        nonlocal passed, total
        total += 1
        if cond:
            passed += 1
            print(f"[PASS] {name}")
        else:
            print(f"[FAIL] {name}")

    setup()

    # 1
    check("FT-SC-01 login admin", sys_login("admin", "admin1234") is True)

    # 2
    check("FT-SC-02 login неверный пароль", sys_login("admin", "wrong") is False)

    # 3
    sys_create_file("/s1.txt", "data", "admin")
    check("FT-SC-03 create_file OK", sys_read_file("/s1.txt", "admin") == "data")

    # 4
    logs = db.execute_select("syscalls_log", {"syscall_name": "sys_create_file"})
    check("FT-SC-04 запись в журнале create", len(logs) >= 1 and logs[0]["status"] == "OK")

    # 5
    check("FT-SC-05 чтение своего", sys_read_file("/s1.txt", "admin") == "data")

    # 6
    check("FT-SC-06 чтение чужого/нет", sys_read_file("/nope.txt", "admin") in (None, ""))

    # 7
    sys_delete_file("/s1.txt", "admin")
    check("FT-SC-07 удаление своего", sys_read_file("/s1.txt", "admin") in (None, ""))

    # 8
    sys_delete_file("/missing.txt", "admin")
    logs = db.execute_select("syscalls_log", {"syscall_name": "sys_delete_file"})
    check("FT-SC-08 отказ логируется", any(l["status"] in ("DENIED", "NOT_FOUND") for l in logs))

    # 9
    pid = sys_exec("app1", "admin")
    check("FT-SC-09 sys_exec возвращает PID", pid is not None)

    # 10
    logs = db.execute_select("syscalls_log", {"syscall_name": "sys_exec"})
    check("FT-SC-10 sys_exec в журнале", len(logs) >= 1)

    # 11
    sys_kill(pid, "admin")
    logs = db.execute_select("syscalls_log", {"syscall_name": "sys_kill"})
    check("FT-SC-11 sys_kill в журнале", len(logs) >= 1)

    print(f"\nПройдено {passed} из {total}")
    return passed == total


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)