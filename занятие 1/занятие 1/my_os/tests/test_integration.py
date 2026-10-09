"""Интеграционные сквозные тесты учебной ОС."""
from src import db, fs, scheduler
from src.auth import register_user
from src.kernel import kernel_instance
from src.syscalls import (
    sys_login, sys_create_file, sys_read_file, sys_delete_file,
    sys_list_files, sys_exec, sys_ps, sys_kill
)

def setup():
    """Подготовка: регистрируем пользователей, очищаем таблицы и сбрасываем состояние ядра."""
    db.init_db()
    
    # Очищаем таблицы перед запуском интеграционных тестов
    db.execute_delete("processes")
    db.execute_delete("files")
    db.execute_delete("users", {"login": "admin"})
    db.execute_delete("users", {"login": "user"})
    
    # Сбрасываем счетчик PID и память в объекте ядра
    kernel_instance.process_counter = 0
    kernel_instance.memory_used = 0
    kernel_instance.save_memory_state()
    
    # Регистрируем тестовых пользователей
    register_user("admin", "secret123", "admin")
    register_user("user", "user1234", "user")
    
def test_login_flow():
    assert sys_login("admin", "secret123") is True
    assert sys_login("admin", "wrong") is False
    assert sys_login("user", "user1234") is True
    print("[PASS] логин: admin и user входят, неверный пароль отклонён")

def test_file_flow():
    fid = sys_create_file("/itest.txt", "hello", "admin")
    assert fid > 0
    assert sys_read_file("/itest.txt", "admin") == "hello"
    assert "/itest.txt" in sys_list_files("/", "admin")
    print("[PASS] файловый поток: создание, чтение, список")

def test_file_duplicate():
    sys_create_file("/dup.txt", "a", "admin")
    result = sys_create_file("/dup.txt", "b", "admin")
    assert result == -1
    print("[PASS] дубликат файла отклонён")

def test_process_flow():
    pid = sys_exec("test_app", "admin")
    assert pid > 0
    processes = sys_ps("admin")
    assert any(p["pid"] == pid for p in processes)
    assert sys_kill(pid, "admin") is True
    print("[PASS] процессный поток: запуск, список, завершение")

def test_permission_delete():
    sys_create_file("/admin_only.txt", "x", "admin")
    owner = fs.get_owner("/admin_only.txt")
    assert owner == "admin"
    assert sys_delete_file("/admin_only.txt", "user") is False
    assert sys_delete_file("/admin_only.txt", "admin") is True
    print("[PASS] права: user не может удалить файл admin")

def test_memory_release():
    before = kernel_instance.memory_used
    pid = sys_exec("memtest", "admin")
    after_create = kernel_instance.memory_used
    sys_kill(pid, "admin")
    after_kill = kernel_instance.memory_used
    assert after_create > before
    assert after_kill == before
    print("[PASS] память выделяется и освобождается")

def test_full_scenario():
    sys_login("admin", "secret123")
    fid = sys_create_file("/scenario.txt", "data", "admin")
    pid = sys_exec("scenario_app", "admin")
    assert fid > 0
    assert pid > 0
    assert sys_read_file("/scenario.txt", "admin") == "data"
    assert sys_kill(pid, "admin") is True
    print("[PASS] сквозной сценарий пройден")

if __name__ == "__main__":
    setup()
    test_login_flow()
    test_file_flow()
    test_file_duplicate()
    test_process_flow()
    test_permission_delete()
    test_memory_release()
    test_full_scenario()
    print("\n[SUCCESS] Все 7 интеграционных тестов пройдены успешно.")