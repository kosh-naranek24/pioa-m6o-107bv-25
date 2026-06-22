# tests/test_memory.py
import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import (
    TableNotFoundError,
    TableAlreadyExistsError,
    MissingColumnError,
    UnknownColumnError,
)


class TestMemoryDatabase(unittest.TestCase):
    """Тесты для MemoryDatabase."""

    def setUp(self):
        """Создание базы данных перед каждым тестом."""
        self.db = MemoryDatabase()
        self.db.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))

    # === Тесты создания таблиц ===

    def test_create_table_success(self):
        """Тест успешного создания таблицы."""
        self.db.create_table("test", ("id", "name"))
        self.assertTrue(self.db._table_exists("test"))

    def test_create_table_already_exists(self):
        """Тест создания уже существующей таблицы."""
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("students", ("id", "name"))

    # === Тесты вставки записей ===

    def test_insert_record_success(self):
        """Тест успешной вставки записи."""
        record = {"student_id": 1, "first_name": "Иван", "second_name": "Петров", "age": 20, "sex": "М"}
        self.db.insert_record("students", record)
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], record)

    def test_insert_record_missing_column(self):
        """Тест вставки с отсутствующим полем."""
        record = {"student_id": 1, "first_name": "Иван"}  # Нет second_name, age, sex
        with self.assertRaises(MissingColumnError):
            self.db.insert_record("students", record)

    def test_insert_record_extra_column(self):
        """Тест вставки с лишним полем."""
        record = {"student_id": 1, "first_name": "Иван", "second_name": "Петров", "age": 20, "sex": "М", "extra": "bad"}
        with self.assertRaises(UnknownColumnError):
            self.db.insert_record("students", record)

    def test_insert_record_table_not_found(self):
        """Тест вставки в несуществующую таблицу."""
        with self.assertRaises(TableNotFoundError):
            self.db.insert_record("nonexistent", {"id": 1})

    # === Тесты выборки записей ===

    def test_select_all_records(self):
        """Тест выборки всех записей."""
        records = [
            {"student_id": 1, "first_name": "Иван", "second_name": "Петров", "age": 20, "sex": "М"},
            {"student_id": 2, "first_name": "Мария", "second_name": "Иванова", "age": 22, "sex": "Ж"},
        ]
        for record in records:
            self.db.insert_record("students", record)

        result = self.db.select_records("students")
        self.assertEqual(len(result), 2)
        self.assertEqual(result, records)

    def test_select_with_filters(self):
        """Тест выборки с фильтрами."""
        records = [
            {"student_id": 1, "first_name": "Иван", "second_name": "Петров", "age": 20, "sex": "М"},
            {"student_id": 2, "first_name": "Мария", "second_name": "Иванова", "age": 22, "sex": "Ж"},
            {"student_id": 3, "first_name": "Иван", "second_name": "Сидоров", "age": 25, "sex": "М"},
        ]
        for record in records:
            self.db.insert_record("students", record)

        result = self.db.select_records("students", first_name="Иван")
        self.assertEqual(len(result), 2)

        result = self.db.select_records("students", first_name="Иван", age=20)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["student_id"], 1)

    def test_select_with_filters_no_results(self):
        """Тест выборки с фильтрами без результатов."""
        self.db.insert_record("students",
                              {"student_id": 1, "first_name": "Иван", "second_name": "Петров", "age": 20, "sex": "М"})

        result = self.db.select_records("students", first_name="Nonexistent")
        self.assertEqual(len(result), 0)

    def test_select_returns_copies(self):
        """Тест: выборка возвращает копии записей."""
        record = {"student_id": 1, "first_name": "Иван", "second_name": "Петров", "age": 20, "sex": "М"}
        self.db.insert_record("students", record)

        result = self.db.select_records("students")
        result[0]["first_name"] = "Изменено"

        # Проверяем, что оригинал не изменился
        original = self.db.select_records("students")
        self.assertEqual(original[0]["first_name"], "Иван")

    def test_select_from_missing_table(self):
        """Тест выборки из несуществующей таблицы."""
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("nonexistent")

    def test_select_with_unknown_column(self):
        """Тест выборки с неизвестной колонкой."""
        with self.assertRaises(UnknownColumnError):
            self.db.select_records("students", unknown="value")

    # === Тесты обновления записей ===

    def test_update_records_success(self):
        """Тест успешного обновления записей."""
        record = {"student_id": 1, "first_name": "Иван", "second_name": "Петров", "age": 20, "sex": "М"}
        self.db.insert_record("students", record)

        updated = self.db.update_records(
            "students",
            filters={"student_id": 1},
            updates={"age": 21, "first_name": "Иванн"}
        )

        self.assertEqual(len(updated), 1)
        records = self.db.select_records("students")
        self.assertEqual(records[0]["age"], 21)
        self.assertEqual(records[0]["first_name"], "Иванн")

    def test_update_records_multiple_matches(self):
        """Тест обновления нескольких записей."""
        records = [
            {"student_id": 1, "first_name": "Иван", "second_name": "Петров", "age": 20, "sex": "М"},
            {"student_id": 2, "first_name": "Иван", "second_name": "Сидоров", "age": 25, "sex": "М"},
            {"student_id": 3, "first_name": "Мария", "second_name": "Иванова", "age": 22, "sex": "Ж"},
        ]
        for record in records:
            self.db.insert_record("students", record)

        updated = self.db.update_records(
            "students",
            filters={"first_name": "Иван"},
            updates={"age": 30}
        )

        self.assertEqual(len(updated), 2)
        records = self.db.select_records("students", first_name="Иван")
        for record in records:
            self.assertEqual(record["age"], 30)

    def test_update_records_empty_filters(self):
        """Тест обновления с пустым фильтром."""
        with self.assertRaises(ValueError):
            self.db.update_records("students", filters={}, updates={"name": "Новое"})

    def test_update_records_unknown_column(self):
        """Тест обновления с неизвестной колонкой."""
        with self.assertRaises(UnknownColumnError):
            self.db.update_records(
                "students",
                filters={"student_id": 1},
                updates={"unknown": "value"}
            )

    def test_update_records_no_matches(self):
        """Тест обновления без совпадений."""
        self.db.insert_record("students",
                              {"student_id": 1, "first_name": "Иван", "second_name": "Петров", "age": 20, "sex": "М"})

        updated = self.db.update_records(
            "students",
            filters={"student_id": 999},
            updates={"age": 30}
        )
        self.assertEqual(updated, [])

    # === Тесты удаления записей ===

    def test_delete_records_success(self):
        """Тест успешного удаления записей."""
        records = [
            {"student_id": 1, "first_name": "Иван", "second_name": "Петров", "age": 20, "sex": "М"},
            {"student_id": 2, "first_name": "Мария", "second_name": "Иванова", "age": 22, "sex": "Ж"},
        ]
        for record in records:
            self.db.insert_record("students", record)

        deleted = self.db.delete_records("students", filters={"student_id": 1})

        self.assertEqual(len(deleted), 1)
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["student_id"], 2)

    def test_delete_records_multiple_matches(self):
        """Тест удаления нескольких записей."""
        records = [
            {"student_id": 1, "first_name": "Иван", "second_name": "Петров", "age": 20, "sex": "М"},
            {"student_id": 2, "first_name": "Иван", "second_name": "Сидоров", "age": 25, "sex": "М"},
            {"student_id": 3, "first_name": "Мария", "second_name": "Иванова", "age": 22, "sex": "Ж"},
        ]
        for record in records:
            self.db.insert_record("students", record)

        deleted = self.db.delete_records("students", filters={"first_name": "Иван"})

        self.assertEqual(len(deleted), 2)
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["first_name"], "Мария")

    def test_delete_records_empty_filters(self):
        """Тест удаления с пустым фильтром."""
        with self.assertRaises(ValueError):
            self.db.delete_records("students", filters={})

    def test_delete_records_unknown_column(self):
        """Тест удаления с неизвестной колонкой."""
        with self.assertRaises(UnknownColumnError):
            self.db.delete_records("students", filters={"unknown": "value"})

    def test_delete_records_no_matches(self):
        """Тест удаления без совпадений."""
        self.db.insert_record("students",
                              {"student_id": 1, "first_name": "Иван", "second_name": "Петров", "age": 20, "sex": "М"})

        deleted = self.db.delete_records("students", filters={"student_id": 999})
        self.assertEqual(deleted, [])
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()