"""Тесты разграничения прав доступа (Permission Tests)."""
from src import db, fs
from src.syscalls import sys_delete_file, sys_kill, sys_exec, sys_create_file

def setup():
    """Подготовка БД перед запуском тестов."""
    db.init_db()
    db.execute_delete("processes")
    db.execute_delete("files")

def test_guest_cannot_delete_admin_file():
    # Создаем файл от имени admin
    sys_create_file("/admin_file.txt", "content", "admin")
    
    # Попытка удаления от имени guest
    result = sys_delete_file("/admin_file.txt", "guest", owner="admin")
    assert result is False, "guest не должен удалять файл admin"
    print("[PASS] TC-02: guest не может удалить файл admin")

def test_admin_can_delete_any_file():
    # Создаем файл от имени user
    sys_create_file("/user_file.txt", "content", "user")
    
    # Администратор удаляет файл пользователя
    result = sys_delete_file("/user_file.txt", "admin", owner="user")
    assert result is True, "admin должен удалять любой файл"
    print("[PASS] admin может удалить файл user")

def test_guest_cannot_kill_process():
    # Создаем процесс для проверки
    pid = sys_exec("test_proc", "admin")
    
    # Попытка завершения от имени guest
    result = sys_kill(pid, "guest")
    assert result is False, "guest не должен убивать процессы"
    print("[PASS] guest не может убить процесс")

def test_admin_can_kill_process():
    # Создаем процесс для завершения
    pid = sys_exec("test_proc_admin", "admin")
    assert pid > 0, "Процесс должен успешно создаться"
    
    # Завершение от имени admin
    result = sys_kill(pid, "admin")
    assert result is True, "admin должен убивать процессы"
    print("[PASS] admin может убить процесс")

if __name__ == "__main__":
    setup()
    test_guest_cannot_delete_admin_file()
    test_admin_can_delete_any_file()
    test_guest_cannot_kill_process()
    test_admin_can_kill_process()
    print("\nВсе тесты пройдены.")