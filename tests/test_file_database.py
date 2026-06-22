import tempfile
import unittest
import json
import os
from src.db.backend.file import FileDatabase
from src.db.backend.errors import (
    TableNotFoundError,
    InvalidStorageDataError
)

class TestFileDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = FileDatabase(self.temp_dir.name)
        self.db.create_table("students", ("student_id", "name", "age"))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_data_persistence(self):
        """Тест сохранения данных между экземплярами"""
        self.db.insert_record("students", {"student_id": 1, "name": "John", "age": 20})

        new_db = FileDatabase(self.temp_dir.name)
        records = new_db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "John")

    def test_table_file_created(self):
        """Тест создания файла таблицы"""
        table_path = os.path.join(self.temp_dir.name, "students.json")
        self.assertTrue(os.path.exists(table_path))

        with open(table_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn("columns", data)
            self.assertIn("records", data)

    def test_select_with_filters(self):
        """Тест выборки с фильтрами"""
        self.db.insert_record("students", {"student_id": 1, "name": "John", "age": 20})
        self.db.insert_record("students", {"student_id": 2, "name": "Jane", "age": 22})

        records = self.db.select_records("students", name="John")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["student_id"], 1)

    def test_update_records(self):
        """Тест обновления записей"""
        self.db.insert_record("students", {"student_id": 1, "name": "John", "age": 20})
        self.db.update_records(
            "students",
            filters={"student_id": 1},
            updates={"name": "Johnny"}
        )

        records = self.db.select_records("students")
        self.assertEqual(records[0]["name"], "Johnny")

    def test_delete_records(self):
        """Тест удаления записей"""
        self.db.insert_record("students", {"student_id": 1, "name": "John", "age": 20})
        self.db.delete_records("students", filters={"student_id": 1})

        records = self.db.select_records("students")
        self.assertEqual(len(records), 0)

    def test_select_from_missing_table(self):
        """Тест выборки из несуществующей таблицы"""
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("nonexistent")

    def test_corrupted_file_handling(self):
        """Тест обработки повреждённого файла"""

        self.db.insert_record("students", {"student_id": 1, "name": "John", "age": 20})

        # Повреждаем файл
        table_path = os.path.join(self.temp_dir.name, "students.json")
        with open(table_path, 'w', encoding='utf-8') as f:
            f.write("not valid json")

        # Создаём новый экземпляр БД
        new_db = FileDatabase(self.temp_dir.name)

        # Ошибка должна возникнуть при обращении к таблице
        with self.assertRaises(InvalidStorageDataError):
            new_db.select_records("students")


    def test_invalid_structure_missing_columns(self):
        """Тест загрузки файла с отсутствующим полем 'columns'"""
        table_path = os.path.join(self.temp_dir.name, "students.json")
        with open(table_path, 'w', encoding='utf-8') as f:
            json.dump({"records": []}, f)

        new_db = FileDatabase(self.temp_dir.name)
        with self.assertRaises(InvalidStorageDataError):
            new_db.select_records("students")


    def test_invalid_structure_missing_records(self):
        """Тест загрузки файла с отсутствующим полем 'records'"""
        table_path = os.path.join(self.temp_dir.name, "students.json")
        with open(table_path, 'w', encoding='utf-8') as f:
            json.dump({"columns": ["id", "name"]}, f)

        new_db = FileDatabase(self.temp_dir.name)
        with self.assertRaises(InvalidStorageDataError):
            new_db.select_records("students")


    def test_os_error_on_save(self):

        from unittest.mock import patch

        with patch('pathlib.Path.open', side_effect=OSError("Permission denied")):
            with self.assertRaises(InvalidStorageDataError):
                self.db.insert_record("students", {"student_id": 99, "name": "Test", "age": 30})

    def test_os_error_on_load(self):
        from unittest.mock import patch

        self.db.insert_record("students", {"student_id": 1, "name": "John", "age": 20})

        with patch('pathlib.Path.open', side_effect=OSError("Permission denied")):
            with self.assertRaises(InvalidStorageDataError):
                self.db.select_records("students")

if __name__ == "__main__":
    unittest.main()