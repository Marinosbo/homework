import os
print("Current working directory:", os.getcwd())
import zipfile
import csv
import configparser
import shutil
import sys
from datetime import datetime
from enum import unique

class Config: #Загрузка конфигурации из ini-файла
    def __init__(self, config_path):
        self.config = configparser.ConfigParser() #Работа с файлами конфигурации
        self.config.read(config_path) #Чтение конфигурации из файла

        self.hostname = self.config["DEFAULT"]["hostname"] #Параметры конфигурации
        self.vfs_path = self.config["DEFAULT"]["vfs_path"]
        self.log_path = self.config["DEFAULT"]["log_path"]
        self.start_script = self.config["DEFAULT"]["start_script"]

class Logger:
    def __init__(self, log_path):
        self.log_path = log_path

    def log_action(self, action, result=""):
        with open(self.log_path, "a", newline="") as log_file:
            writer = csv.writer(log_file)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action, result])

class VirtualFileSystem:
    def __init__(self, zip_path):
        self.root_path = "vfs_temp"                     # Путь корневой виртуальной файловой системе
        self.load_vfs(zip_path)                         # Разархировать файловую систему для инициализации
        self.current_path = self.root_path              # Установка начальной директории
    def load_vfs(self, zip_path):                       # Загрузка и разархивирование файловой системы из зип архива
        if os.path.exists(self.root_path):              # Удаление предыдущей директории(если существ)
            shutil.rmtree(self.root_path)
        with zipfile.ZipFile(zip_path, "r") as zip_ref: #И
            zip_ref.extractall(self.root_path)

    def ls(self):                                       # Команда ls: выводит содержимое текущей директории
        return "\n".join(os.listdir(self.current_path)) #Разделитель

    def cd(self, target_path):                          # Команда cd: изменяет текущую директорию
        new_path = os.path.join(self.current_path, target_path)
        if os.path.isdir(new_path):
            self.current_path = new_path
        else:
            raise NotADirectoryError(f"{target_path} is not a directory")

    def tac(self, file_path):                           # Команда tac: выводит содержимое файла в обратном порядке строк
        full_path = os.path.join(self.current_path, file_path)
        with open(full_path, "r") as file:
            lines = file.readlines()
        return "".join(reversed(lines))

    def mv(self, source, destination):
        source_path = os.path.join(self.current_path, source)
        destination_path = os.path.join(self.current_path, destination)
        print(f"Attempting to move '{source_path}' to '{destination_path}'")  # Добавлено
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file '{source}' not found.")
        shutil.move(source_path, destination_path)
        print(f"Moved '{source_path}' to '{destination_path}'")  # Добавлено

    def uniq(self, file_path):                          # Удаляет дублирующиеся строки в файле
        full_path = os.path.join(self.current_path, file_path)
        with open(full_path, "r") as file:
            lines = file.readlines()
        unique_lines = []
        [unique_lines.append(line) for line in lines if line not in unique_lines]
        return "".join(unique_lines)
class ShellEmulator:
    def __init__(self, config_path):
        self.config = Config(config_path)  # Сначала инициализируем self.config
        print("Config path:", config_path)  # Печатаем путь к config.ini
        print("VFS path from config:", self.config.vfs_path)  # Проверяем значение vfs_path

        self.logger = Logger(self.config.log_path)  # Логгер
        self.vfs = VirtualFileSystem(self.config.vfs_path)  # Виртуальная ФС
        self.hostname = self.config.hostname  # Имя компьютера

    def execute_command(self, command):                  # Метод для выполнения команд
        parts = command.split()
        cmd = parts[0]
        args = parts[1:]

        # Проверка команды и вызов соответствующего метода
        if cmd == "ls":
            return self.vfs.ls()
        elif cmd == "cd":
            self.vfs.cd(args[0] if args else ".")
            return f"Changed directory to {self.vfs.current_path}"
        elif cmd == "tac":
            return self.vfs.tac(args[0])
        elif cmd =="mv":
            return f"Moved {args[0]} to {args[1]}"
        elif cmd == "uniq":
            return self.vfs.uniq(args[0])
        elif cmd == "exit":
            sys.exit(0)
        else:
            return "Command not found"
    def run_start_sqript(self):
        if os.path.exists(self.config.start_script):
            with open(self.config.start_script, "r") as script_file:
                for line in script_file:
                    line = line.scrip()
                    print(f"$ {line}")
                    result = self.execute_command(line)
                    print(result)
                    self.logger.log_action(line, result)
    def run(self):
        self.run_start_sqript()
        while True:
            command = input(f"{self.hostname}:{self.vfs.current_path}$" )
            try:
                result = self.execute_command(command)
                print(result)
                self.logger.log_action(command, result)
            except Exception as e:
                print(f"Error: {e}")
                self.logger.log_action(f"Error: {e}")
if __name__ == "__main__":
    config_path = "config.ini"
    shell = ShellEmulator(config_path)
    shell.run()