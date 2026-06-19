import unittest
from src.db.backend.table import Table
from src.db.backend.errors import MissingColumnError, UnknownColumnError


class TestTable(unittest.TestCase):
    def setUp(self):
        self.columns = ("student_id", "name", "age")
        self.table = Table(self.columns)

    def test_insert_valid_record(self):
        """Тест вставки корректной записи"""
        record = {"student_id": 1, "name": "John", "age": 20}
        self.table.insert_record(record)
        self.assertEqual(len(self.table.records), 1)
        self.assertEqual(self.table.records[0], record)

    def test_insert_missing_column(self):
        """Тест вставки с отсутствующим полем"""
        record = {"student_id": 1, "name": "John"}
        with self.assertRaises(MissingColumnError):
            self.table.insert_record(record)

    def test_insert_extra_column(self):
        """Тест вставки с лишним полем"""
        record = {"student_id": 1, "name": "John", "age": 20, "extra": "bad"}
        with self.assertRaises(UnknownColumnError):
            self.table.insert_record(record)

    def test_select_all(self):
        """Тест выборки всех записей"""
        self.table.insert_record({"student_id": 1, "name": "John", "age": 20})
        self.table.insert_record({"student_id": 2, "name": "Jane", "age": 22})
        results = self.table.select_records()
        self.assertEqual(len(results), 2)

    def test_select_with_filters(self):
        """Тест выборки с фильтрами"""
        self.table.insert_record({"student_id": 1, "name": "John", "age": 20})
        self.table.insert_record({"student_id": 2, "name": "Jane", "age": 22})
        results = self.table.select_records(name="John")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["student_id"], 1)

    def test_select_with_multiple_filters(self):
        """Тест выборки с несколькими фильтрами"""
        self.table.insert_record({"student_id": 1, "name": "John", "age": 20})
        self.table.insert_record({"student_id": 2, "name": "John", "age": 22})
        results = self.table.select_records(name="John", age=20)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["student_id"], 1)

    def test_select_unknown_column(self):
        """Тест выборки с неизвестной колонкой"""
        with self.assertRaises(UnknownColumnError):
            self.table.select_records(unknown="value")

    def test_update_records(self):
        """Тест обновления записей"""
        self.table.insert_record({"student_id": 1, "name": "John", "age": 20})
        updated = self.table.update_records(
            filters={"student_id": 1},
            updates={"name": "Johnny", "age": 21}
        )
        self.assertEqual(len(updated), 1)
        self.assertEqual(self.table.records[0]["name"], "Johnny")
        self.assertEqual(self.table.records[0]["age"], 21)

    def test_update_records_empty_filters(self):
        """Тест обновления с пустым фильтром"""
        self.table.insert_record({"student_id": 1, "name": "John", "age": 20})
        with self.assertRaises(ValueError):
            self.table.update_records(filters={}, updates={"name": "Johnny"})

    def test_update_records_unknown_column(self):
        """Тест обновления с неизвестной колонкой"""
        self.table.insert_record({"student_id": 1, "name": "John", "age": 20})
        with self.assertRaises(UnknownColumnError):
            self.table.update_records(
                filters={"student_id": 1},
                updates={"unknown": "value"}
            )

    def test_update_records_no_matches(self):
        """Тест обновления без совпадений"""
        self.table.insert_record({"student_id": 1, "name": "John", "age": 20})
        updated = self.table.update_records(
            filters={"student_id": 999},
            updates={"name": "Johnny"}
        )
        self.assertEqual(updated, [])
        self.assertEqual(self.table.records[0]["name"], "John")

    def test_delete_records(self):
        """Тест удаления записей"""
        self.table.insert_record({"student_id": 1, "name": "John", "age": 20})
        self.table.insert_record({"student_id": 2, "name": "Jane", "age": 22})
        deleted = self.table.delete_records(filters={"student_id": 1})
        self.assertEqual(len(deleted), 1)
        self.assertEqual(len(self.table.records), 1)
        self.assertEqual(self.table.records[0]["student_id"], 2)

    def test_delete_records_empty_filters(self):
        """Тест удаления с пустым фильтром"""
        self.table.insert_record({"student_id": 1, "name": "John", "age": 20})
        with self.assertRaises(ValueError):
            self.table.delete_records(filters={})

    def test_delete_records_unknown_column(self):
        """Тест удаления с неизвестной колонкой"""
        self.table.insert_record({"student_id": 1, "name": "John", "age": 20})
        with self.assertRaises(UnknownColumnError):
            self.table.delete_records(filters={"unknown": "value"})

    def test_delete_records_no_matches(self):
        """Тест удаления без совпадений"""
        self.table.insert_record({"student_id": 1, "name": "John", "age": 20})
        deleted = self.table.delete_records(filters={"student_id": 999})
        self.assertEqual(deleted, [])
        self.assertEqual(len(self.table.records), 1)

if __name__ == "__main__":
    unittest.main()