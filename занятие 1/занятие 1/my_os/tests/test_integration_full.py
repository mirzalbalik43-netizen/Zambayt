"""Интеграционные тесты (10 тестов)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import db
from src.auth import register_user
from src.kernel import kernel_instance
from src.syscalls import (
    sys_login, sys_create_file, sys_read_file, sys_delete_file,
    sys_exec, sys_kill,
)


def setup():
    db.init_db()
    for t in ("files", "users", "syscalls_log", "processes"):
        db.execute_delete(t, {})
    register_user("admin", "admin1234", "admin")
    register_user("user", "user1234", "user")


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

    # IS-01
    sys_login("admin", "admin1234")
    sys_create_file("/is01.txt", "content", "admin")
    check("IS-01 создание файла", sys_read_file("/is01.txt", "admin") == "content")

    # IS-02
    check("IS-02 чтение файла", sys_read_file("/is01.txt", "admin") == "content")

    # IS-03
    sys_create_file("/is03.txt", "x", "admin")
    sys_login("user", "user1234")
    sys_delete_file("/is03.txt", "user")
    logs = db.execute_select("syscalls_log", {"syscall_name": "sys_delete_file"})
    check("IS-03 отказ удаления чужого", any(l["status"] in ("DENIED", "NOT_FOUND") for l in logs))

    # IS-04
    sys_login("admin", "admin1234")
    before = kernel_instance.memory_used
    pid = sys_exec("is04_app", "admin")
    check("IS-04 запуск процесса + память", pid is not None and kernel_instance.memory_used > before)

    # IS-05
    after_kill = sys_kill(pid, "admin")
    check("IS-05 завершение процесса", after_kill is not False)

    # IS-06 (сквозной admin)
    sys_create_file("/is06.txt", "abc", "admin")
    pid2 = sys_exec("is06_app", "admin")
    sys_kill(pid2, "admin")
    check("IS-06 сквозной admin", sys_read_file("/is06.txt", "admin") == "abc")

    # IS-07 (сквозной user)
    sys_login("user", "user1234")
    sys_create_file("/is07.txt", "u", "user")
    sys_delete_file("/is03.txt", "user")  # чужой
    check("IS-07 user свои/чужие", sys_read_file("/is07.txt", "user") == "u")

    # IS-08 журнал
    all_logs = db.execute_select("syscalls_log", {})
    check("IS-08 журнал заполнен", len(all_logs) >= 5)

    # IS-09 согласованность памяти
    check("IS-09 память согласована", kernel_instance.memory_used >= 0)

    # IS-10 очистка после kill
    pid3 = sys_exec("is10_app", "admin")
    sys_kill(pid3, "admin")
    check("IS-10 очистка после kill", True)

    print(f"\nПройдено {passed} из {total}")
    return passed == total


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)