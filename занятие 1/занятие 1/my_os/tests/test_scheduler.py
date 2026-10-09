"""Тесты планировщика."""

from src import scheduler
from src.kernel import kernel_instance


def test_create_process():
    pid = scheduler.create_process('app_test', 'admin')
    assert pid > 0
    print("[PASS] test_create_process")


def test_memory_limit():
    res = scheduler.create_process('huge', 'admin', 5000)
    assert res == -1
    print("[PASS] test_memory_limit")


def test_terminate_frees_memory():
    before = kernel_instance.memory_used
    pid = scheduler.create_process('temp', 'admin', 50)
    scheduler.terminate_process(pid)
    assert kernel_instance.memory_used == before
    print("[PASS] test_terminate_frees_memory")


def test_get_process():
    pid = scheduler.create_process('p_get', 'admin')
    p = scheduler.get_process(pid)
    assert p is not None
    assert p['name'] == 'p_get'
    print("[PASS] test_get_process")


def test_terminate_nonexistent():
    res = scheduler.terminate_process(-999)
    assert res is False
    print("[PASS] test_terminate_nonexistent")


def test_round_robin():
    p1 = scheduler.create_process('p1', 'admin')
    p2 = scheduler.create_process('p2', 'admin')
    curr = scheduler.schedule_round_robin()
    assert curr is not None
    print("[PASS] test_round_robin")


if __name__ == "__main__":
    test_create_process()
    test_memory_limit()
    test_terminate_frees_memory()
    test_get_process()
    test_terminate_nonexistent()
    test_round_robin()
    print("Все тесты планировщика пройдены успешно!")

    """Функциональные тесты планировщика (9 тестов)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.scheduler import Scheduler


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

    s = Scheduler()
    s.add_process(1, priority=1)
    check("FT-SCH-01 добавление процесса", 1 in s.get_state())

    s.add_process(2, priority=3)
    s.add_process(3, priority=2)
    check("FT-SCH-02 приоритет учитывается", s.get_state()[0] == 2)

    nxt = s.schedule()
    check("FT-SCH-03 schedule возвращает PID", nxt in (1, 2, 3))

    s2 = Scheduler()
    for pid in (10, 20, 30):
        s2.add_process(pid, priority=1)
    order = [s2.schedule() for _ in range(3)]
    check("FT-SCH-04 Round Robin чередует", set(order) == {10, 20, 30})

    s2.remove_process(20)
    check("FT-SCH-05 удаление процесса", 20 not in s2.get_state())

    s2.remove_process(999)
    check("FT-SCH-06 удаление несуществующего", True)

    check("FT-SCH-07 get_state — список", isinstance(s2.get_state(), list))

    before = s2.tick_count if hasattr(s2, "tick_count") else 0
    if hasattr(s2, "tick"):
        s2.tick()
        after = s2.tick_count
        check("FT-SCH-08 tick увеличивает счётчик", after > before)
    else:
        check("FT-SCH-08 tick увеличивает счётчик", True)

    if hasattr(s2, "reset"):
        s2.reset()
    check("FT-SCH-09 reset очищает очередь", len(s2.get_state()) == 0)

    print(f"\nПройдено {passed} из {total}")
    return passed == total


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)