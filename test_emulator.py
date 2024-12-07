import unittest
import os
import shutil
from shell_emulator import ShellEmulator


class TestShellEmulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Создаем тестовую виртуальную файловую систему
        cls.vfs_root = "vfs_temp"
        if os.path.exists(cls.vfs_root):
            shutil.rmtree(cls.vfs_root)
        os.makedirs(cls.vfs_root)

        # Создаем поддиректорию
        cls.subdir = os.path.join(cls.vfs_root, "subdir")
        os.makedirs(cls.subdir)

        # Создаем файл test.txt
        cls.test_file = os.path.join(cls.vfs_root, "test.txt")
        with open(cls.test_file, "w") as f:
            f.write("line1\nline2\nline1\n")

        # Создаем start_script.txt
        cls.start_script = os.path.join(cls.vfs_root, "start_script.txt")
        with open(cls.start_script, "w") as f:
            f.write("ls\ncd subdir\nls\ntac ../test.txt\nmv ../test.txt moved_test.txt\nuniq moved_test.txt\nexit\n")

        # Создаем zip-архив VFS
        shutil.make_archive("test_vfs", 'zip', cls.vfs_root)

        # Создаем config.ini
        with open("test_config.ini", "w") as f:
            f.write("[DEFAULT]\n")
            f.write("hostname = test_host\n")
            f.write("vfs_path = test_vfs.zip\n")
            f.write("log_path = test_log.csv\n")
            f.write("start_script = start_script.txt\n")

    @classmethod
    def tearDownClass(cls):
        # Удаляем созданные тестовые файлы и директории
        if os.path.exists(cls.vfs_root):
            shutil.rmtree(cls.vfs_root)
        if os.path.exists("test_vfs.zip"):
            os.remove("test_vfs.zip")
        if os.path.exists("test_config.ini"):
            os.remove("test_config.ini")
        if os.path.exists("test_log.csv"):
            os.remove("test_log.csv")
        if os.path.exists("moved_test.txt"):
            os.remove("moved_test.txt")

    def setUp(self):
        # Создаем экземпляр ShellEmulator с тестовой конфигурацией
        self.shell = ShellEmulator("test_config.ini")

    def tearDown(self):
        # Перезагружаем VFS после каждого теста
        self.shell.vfs.load_vfs(self.shell.config.vfs_path)

    def test_ls(self):
        # Проверяем команду ls в корневой директории
        result = self.shell.execute_command("ls")
        self.assertIn("subdir", result)
        self.assertIn("test.txt", result)

    def test_cd(self):
        # Проверяем команду cd
        result = self.shell.execute_command("cd subdir")
        self.assertEqual(self.shell.vfs.current_path, os.path.join(self.shell.vfs.root_path, "subdir"))

    def test_exit(self):
        # Проверяем завершение программы командой exit
        with self.assertRaises(SystemExit):
            self.shell.execute_command("exit")

    def test_tac(self):
        # Проверяем команду tac
        result = self.shell.execute_command("tac test.txt")
        expected = "line1\nline2\nline1\n"[::-1]  # Неправильная логика, исправим ниже
        # Корректное ожидание: строки в обратном порядке
        expected_correct = "line1\nline2\nline1\n"[::-1].replace('\n', '\n')  # Исправим позже
        # Правильный способ: "line1\nline2\nline1\n" -> "line1\nline2\nline1\n" reversed by lines
        expected_correct = "line1\nline2\nline1\n"[::-1]  # Это не правильно, исправим
        # Исправление:
        expected_correct = "line1\nline2\nline1\n"
        # Но правильный результат от tac будет:
        expected_correct = "line1\nline2\nline1\n"  # Исправить ниже
        # Wait, let's see:
        # Original lines: ["line1\n", "line2\n", "line1\n"]
        # Reversed lines: ["line1\n", "line2\n", "line1\n"] -> ["line1\n", "line2\n", "line1\n"]
        # This is same as original, because first and last lines are same
        self.assertEqual(result, "line1\nline2\nline1\n")

    def test_tac_invalid(self):
        # Проверяем команду tac с несуществующим файлом
        with self.assertRaises(FileNotFoundError):
            self.shell.execute_command("tac non_existent_file.txt")

    def test_mv(self):
        # Проверяем команду mv (переименование)
        result = self.shell.execute_command("mv test.txt moved_test.txt")
        self.assertTrue(os.path.exists(os.path.join(self.shell.vfs.current_path, "moved_test.txt")))
        self.assertFalse(os.path.exists(os.path.join(self.shell.vfs.current_path, "test.txt")))

    def test_mv_invalid(self):
        # Проверяем команду mv с несуществующим файлом
        with self.assertRaises(FileNotFoundError):
            self.shell.execute_command("mv non_existent_file.txt destination.txt")

    def test_uniq(self):
        # Проверяем команду uniq
        # Сначала переименуем test.txt в moved_test.txt для подготовки
        self.shell.execute_command("mv test.txt moved_test.txt")
        result = self.shell.execute_command("uniq moved_test.txt")
        self.assertEqual(result, "line1\nline2\n")

    def test_uniq_invalid(self):
        # Проверяем команду uniq с несуществующим файлом
        with self.assertRaises(FileNotFoundError):
            self.shell.execute_command("uniq non_existent_file.txt")


if __name__ == '__main__':
    unittest.main()
