"""Модуль аутентификации и разграничения прав доступа."""
import hashlib
from src import db

def hash_password(password):
    """Хэширование пароля алгоритмом SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register_user(login, password, role="user"):
    """Регистрация нового пользователя."""
    existing = db.execute_select("users", {"login": login})
    if existing:
        return None
    return db.execute_insert("users", {
        "login": login,
        "password_hash": hash_password(password),
        "role": role
    })

def authenticate(login, password):
    """Аутентификация пользователя."""
    users = db.execute_select("users", {"login": login})
    if not users:
        return None
    user = users[0]
    if user["password_hash"] == hash_password(password):
        return user
    return None

def check_permission(current_user, action, target_owner=None):
    """Проверка прав доступа пользователя к объектам и операциям."""
    if current_user == "admin":
        return True
    users = db.execute_select("users", {"login": current_user})
    if not users and current_user != "guest":
        return False
    role = users[0]["role"] if users else "user"
    if role == "admin":
        return True
    if action in ("delete_file", "kill") and target_owner and target_owner != current_user:
        return False
    if action == "kill" and current_user != "admin":
        return False
    return True