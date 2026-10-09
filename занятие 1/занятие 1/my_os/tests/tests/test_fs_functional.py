"""Функциональные тесты файловой системы (10 тестов)."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import db
from src.fs import create_file, read_file, delete_file, list_files


def setup():
    db.init_db()
    db.execute_delete("files", {})


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
    fid = create_file("/f1.txt", "hello", "admin")
    check("FT-FS-01 create_file возвращает id", fid is not None)

    # 2
    fid2 = create_file("/f1.txt", "again", "admin")
    check("FT-FS-02 повторное создание отклонено", fid2 is None)

    # 3
    row = db.execute_select("files", {"path": "/f1.txt"})
    check("FT-FS-03 владелец сохранён", row and row[0]["owner"] == "admin")

    # 4
    paths = [f["path"] for f in list_files("admin")]
    check("FT-FS-04 файл в списке", "/f1.txt" in paths)

    # 5
    check("FT-FS-05 чтение своего файла", read_file("/f1.txt", "admin") == "hello")

    # 6
    create_file("/f6.txt", "secret", "other")
    check("FT-FS-06 чтение чужого отклонено", read_file("/f6.txt", "admin") in (None, ""))

    # 7
    check("FT-FS-07 чтение несуществующего", read_file("/nope.txt", "admin") in (None, ""))

    # 8
    create_file("/f8.txt", "x", "admin")
    delete_file("/f8.txt", "admin")
    check("FT-FS-08 удаление своего файла", not db.execute_select("files", {"path": "/f8.txt"}))

    # 9
    create_file("/f9.txt", "x", "admin")
    delete_file("/f9.txt", "user")
    check("FT-FS-09 удаление чужого отклонено", bool(db.execute_select("files", {"path": "/f9.txt"})))

    # 10
    create_file("/f10a.txt", "a", "admin")
    create_file("/f10b.txt", "b", "user")
    admin_paths = [f["path"] for f in list_files("admin")]
    check("FT-FS-10 список только своих", "/f10a.txt" in admin_paths and "/f10b.txt" not in admin_paths)

    print(f"\nПройдено {passed} из {total}")
    return passed == total


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)