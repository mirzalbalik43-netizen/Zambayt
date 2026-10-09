"""Запуск всех тестов проекта."""
import subprocess
import sys

TESTS = [
    "tests.test_db",
    "tests.test_kernel_unit",
    "tests.test_auth_unit",
    "tests.test_fs_functional",
    "tests.test_scheduler_functional",
    "tests.test_syscalls_functional",
    "tests.test_integration_full",
    "tests.test_stress",
]


def run_test(module):
    print(f"\n{'=' * 60}")
    print(f"Запуск: {module}")
    print("=" * 60)
    result = subprocess.run(
        [sys.executable, "-m", module],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.returncode == 0


if __name__ == "__main__":
    passed = 0
    failed = 0
    failed_tests = []
    for test in TESTS:
        if run_test(test):
            passed += 1
        else:
            failed += 1
            failed_tests.append(test)

    print(f"\n{'=' * 60}")
    print(f"ИТОГО: пройдено {passed}, провалено {failed}")
    if failed_tests:
        print("Проваленные тесты:")
        for t in failed_tests:
            print(f" - {t}")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)