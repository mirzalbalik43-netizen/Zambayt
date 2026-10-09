"""Тесты файловой системы."""

from src import fs


def test_create_and_read():
    fs.create_file('/f1.txt', 'content1', 'admin')
    assert fs.read_file('/f1.txt') == 'content1'
    print("[PASS] test_create_and_read")


def test_duplicate_path():
    fs.create_file('/dup.txt', '1', 'admin')
    res = fs.create_file('/dup.txt', '2', 'admin')
    assert res == -1
    print("[PASS] test_duplicate_path")


def test_update():
    fs.create_file('/up.txt', 'old', 'admin')
    fs.write_file('/up.txt', 'new')
    assert fs.read_file('/up.txt') == 'new'
    print("[PASS] test_update")


def test_delete():
    fs.create_file('/del.txt', 'del', 'admin')
    fs.delete_file('/del.txt')
    assert fs.read_file('/del.txt') == ""
    print("[PASS] test_delete")


def test_owner():
    fs.create_file('/own.txt', '1', 'admin')
    assert fs.get_owner('/own.txt') == 'admin'
    assert fs.get_owner('/non_exist.txt') is None
    print("[PASS] test_owner")


def test_list():
    fs.create_file('/dir/f1.txt', '1', 'admin')
    fs.create_file('/dir/f2.txt', '2', 'admin')
    files = fs.list_files('/dir')
    assert '/dir/f1.txt' in files
    assert '/dir/f2.txt' in files
    print("[PASS] test_list")


if __name__ == "__main__":
    test_create_and_read()
    test_duplicate_path()
    test_update()
    test_delete()
    test_owner()
    test_list()
    print("Все тесты ФС пройдены успешно!")