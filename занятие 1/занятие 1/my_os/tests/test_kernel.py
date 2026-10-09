from src.kernel import kernel_instance

def test_kernel_memory():
    assert kernel_instance.allocate_memory(10) is True
    assert kernel_instance.memory_info()["used"] >= 10
    print("[PASS] test_kernel_memory")

if __name__ == "__main__":
    test_kernel_memory()