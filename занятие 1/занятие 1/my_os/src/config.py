"""Конфигурация и константы учебной ОС."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "os.sqlite")
MEMORY_LIMIT = 1024  # Лимит оперативной памяти в МБ
MAX_MODULE_LINES = 300  # Требование NFR-6 к размеру модуля