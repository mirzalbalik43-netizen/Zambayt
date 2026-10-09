import unittest
from src.syscalls import sys_echo

class TestOS(unittest.TestCase):
    def test_sys_echo(self):
        result = sys_echo("Hello World", user="admin")
        self.assertEqual(result, "Hello World")

if __name__ == "__main__":
    unittest.main()