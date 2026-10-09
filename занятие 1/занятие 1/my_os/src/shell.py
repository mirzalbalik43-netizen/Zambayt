"""Командная оболочка Пользовательского Пространства (User Space)."""
from src.db import init_db
from src.auth import register_user
from src.kernel import kernel_instance
from src.syscalls import (
    sys_login, sys_logout, sys_whoami, sys_create_file, sys_read_file,
    sys_delete_file, sys_list_files, sys_exec, sys_ps, sys_kill,
    sys_logs, sys_shutdown
)

def main():
    init_db()
    # Инициализация дефолтных аккаунтов при первом запуске
    register_user("admin", "secret123", "admin")
    register_user("user", "user1234", "user")

    current_user = "guest"
    print("=" * 50)
    print("      Добро пожаловать в StudyOS v1.0!")
    print("   Введите 'help' для списка доступных команд.")
    print("=" * 50)

    while True:
        try:
            line = input(f"{current_user}@studyos:~$ ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nЗавершение сеанса...")
            break

        if not line:
            continue

        parts = line.split(maxsplit=1)
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "help":
            print("Доступные команды:")
            print("  help                 - вывод справки")
            print("  whoami               - текущий пользователь")
            print("  login                - войти в систему")
            print("  logout               - выйти из системы")
            print("  create               - создать файл (запросит путь и содержимое)")
            print("  cat <path>           - прочитать файл")
            print("  ls [prefix]          - список файлов")
            print("  delete <path>        - удалить файл")
            print("  run <app_name>       - запустить новый процесс")
            print("  ps                   - список запущенных процессов")
            print("  kill <pid>           - завершить процесс")
            print("  mem                  - статистика оперативной памяти")
            print("  logs                 - просмотр журнала системных вызовов")
            print("  exit                 - завершить работу ОС")

        elif cmd == "whoami":
            print(sys_whoami(current_user))

        elif cmd == "login":
            login = input("Логин: ").strip()
            password = input("Пароль: ").strip()
            if sys_login(login, password, current_user):
                current_user = login
                print(f"Вы успешно вошли как '{login}'")
            else:
                print("Ошибка входа: неверный логин или пароль")

        elif cmd == "logout":
            sys_logout(current_user)
            current_user = "guest"
            print("Вы вышли из системы.")

        elif cmd == "create":
            path = input("Путь к файлу: ").strip()
            content = input("Содержимое: ")
            fid = sys_create_file(path, content, current_user)
            if fid == -1:
                print("Ошибка: файл с таким путём уже существует.")
            else:
                print(f"Файл успешно создан (ID={fid})")

        elif cmd == "cat":
            if not arg:
                print("Укажите путь к файлу")
            else:
                c = sys_read_file(arg, current_user)
                print(c if c else "(файл пуст или не существует)")

        elif cmd == "ls":
            files = sys_list_files(arg or "/", current_user)
            if not files:
                print("(файлы не найдены)")
            else:
                for f in files:
                    print(f"  {f}")

        elif cmd == "delete":
            if not arg:
                print("Укажите путь к файлу")
            else:
                if sys_delete_file(arg, current_user):
                    print("Файл успешно удалён.")
                else:
                    print("Ошибка удаления: нет прав или файл не найден.")

        elif cmd == "run":
            if not arg:
                print("Укажите имя приложения")
            else:
                pid = sys_exec(arg, current_user)
                if pid == -1:
                    print("Не удалось запустить процесс: превышен лимит памяти.")
                else:
                    print(f"Запущен процесс PID={pid}")

        elif cmd == "ps":
            procs = sys_ps(current_user)
            if not procs:
                print("(нет активных процессов)")
            else:
                for p in procs:
                    print(f"  PID: {p['pid']} | App: {p['name']} | State: {p['state']} | Owner: {p['owner']} | Mem: {p['memory_used']}MB")

        elif cmd == "kill":
            if not arg:
                print("Укажите PID процесса")
            else:
                try:
                    pid = int(arg)
                    if sys_kill(pid, current_user):
                        print(f"Процесс PID={pid} завершён.")
                    else:
                        print(f"Не удалось завершить процесс PID={pid} (нет прав или PID не существует)")
                except ValueError:
                    print("PID должен быть целым числом.")

        elif cmd == "mem":
            info = kernel_instance.memory_info()
            print(f"Использовано памяти: {info['used']} / {info['limit']} МБ (Свободно: {info['free']} МБ)")

        elif cmd == "logs":
            logs = sys_logs(10, current_user)
            for l in logs:
                print(f"[{l['timestamp']}] {l['user']} -> {l['syscall_name']}({l['args']}) : {l['status']}")

        elif cmd == "exit":
            sys_shutdown(current_user)
            print("Завершение работы системы...")
            break

        else:
            print(f"Неизвестная команда '{cmd}'. Введите 'help'.")

if __name__ == "__main__":
    main()