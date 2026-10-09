"""Модуль виртуальной файловой системы."""
from src import db

def create_file(path, content, owner):
    """Создание файла в ФС."""
    existing = db.execute_select("files", {"path": path})
    if existing:
        return -1
    return db.execute_insert("files", {
        "path": path,
        "content": content,
        "owner": owner
    })

def read_file(path):
    """Чтение содержимого файла."""
    files = db.execute_select("files", {"path": path})
    if not files:
        return ""
    return files[0]["content"]

def write_file(path, content):
    """Перезапись содержимого файла."""
    db.execute_update("files", {"content": content}, {"path": path})
    return True

def delete_file(path):
    """Удаление файла."""
    db.execute_delete("files", {"path": path})
    return True

def list_files(prefix=""):
    """Просмотр списка файлов."""
    all_files = db.execute_select("files")
    return [f["path"] for f in all_files if f["path"].startswith(prefix)]

def get_owner(path):
    """Получение владельца файла."""
    files = db.execute_select("files", {"path": path})
    if not files:
        return None
    return files[0]["owner"]