"""Ядро операционной системы."""
from src import db
from src.config import MEMORY_LIMIT

class Kernel:
    def __init__(self):
        self.current_user = "guest"
        self.process_counter = 0
        self.memory_used = 0
        self.memory_limit = MEMORY_LIMIT

    def set_user(self, login):
        self.current_user = login

    def get_user(self):
        return self.current_user

    def allocate_pid(self):
        """Выдает следующий уникальный PID."""
        procs = db.execute_select("processes")
        if procs:
            max_pid = max(p["pid"] for p in procs)
            self.process_counter = max(self.process_counter, max_pid)
        
        self.process_counter += 1
        return self.process_counter

    def allocate_memory(self, size):
        if self.memory_used + size > self.memory_limit:
            return False
        self.memory_used += size
        self.save_memory_state()
        return True

    def free_memory(self, size):
        self.memory_used = max(0, self.memory_used - size)
        self.save_memory_state()

    def memory_info(self):
        return {
            "used": self.memory_used,
            "limit": self.memory_limit,
            "free": self.memory_limit - self.memory_used
        }

    def save_memory_state(self):
        db.execute_delete("memory_state")
        db.execute_insert("memory_state", {
            "used": self.memory_used,
            "limit_val": self.memory_limit
        })

    def load_memory_state(self):
        states = db.execute_select("memory_state")
        if states:
            self.memory_used = states[0]["used"]
            self.memory_limit = states[0]["limit_val"]

kernel_instance = Kernel()