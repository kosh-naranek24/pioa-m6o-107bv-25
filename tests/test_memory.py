import unittest
from src.db.backend.memory import StudentTable
from src.db.backend.errors import (
    InvalidAgeError,
    DuplicateIDError,
    StudentNotFoundError,
)


class TestStudentTable(unittest.TestCase):

    def setUp(self):
        """Создание пустой таблицы перед каждым тестом."""
        self.table = StudentTable()

    def tearDown(self):
        """Очистка после каждого теста."""
        self.table.clear()

    def _create_test_data(self):
        """Создание тестовых данных."""
        test_data = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
        ]
        for data in test_data:
            self.table.create_record(*data)
        return test_data

    # create_record

    def test_create_record_success(self):
        record = self.table.create_record(1, "John", "Doe", 20, "M")
        self.assertEqual(record, (1, "John", "Doe", 20, "M"))
        self.assertEqual(self.table.count(), 1)

    def test_create_record_with_spaces(self):
        record = self.table.create_record(1, "  John  ", "  Doe  ", 20, "  M  ")
        self.assertEqual(record, (1, "John", "Doe", 20, "M"))

    def test_create_record_duplicate_id(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        with self.assertRaises(DuplicateIDError) as ctx:
            self.table.create_record(1, "Jane", "Smith", 22, "F")
        self.assertIn("Запись с id=1 уже существует", str(ctx.exception))

    def test_create_record_negative_age(self):
        with self.assertRaises(InvalidAgeError) as ctx:
            self.table.create_record(1, "John", "Doe", -5, "M")
        self.assertIn("Некорректный возраст: -5", str(ctx.exception))

    def test_create_record_age_zero(self):
        record = self.table.create_record(1, "John", "Doe", 0, "M")
        self.assertEqual(record, (1, "John", "Doe", 0, "M"))

    def test_create_record_empty_name(self):
        record = self.table.create_record(1, "", "", 20, "M")
        self.assertEqual(record, (1, "", "", 20, "M"))

    # select_record

    def test_select_all_records(self):
        """Выборка всех записей."""
        test_data = self._create_test_data()
        records = self.table.select_record()
        self.assertEqual(len(records), 5)
        self.assertEqual(records, test_data)

    def test_select_returns_copy(self):
        """Без фильтров возвращается копия, а не ссылка."""
        self._create_test_data()
        records = self.table.select_record()
        records.append((999, "Test", "Test", 99, "M"))
        self.assertEqual(self.table.count(), 5)

    def test_select_by_id(self):
        self._create_test_data()
        records = self.table.select_record(student_id=1)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][0], 1)

    def test_select_by_first_name(self):
        self._create_test_data()
        records = self.table.select_record(first_name="Jane")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "Jane")

    def test_select_by_second_name(self):
        self._create_test_data()
        records = self.table.select_record(second_name="Johnson")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][2], "Johnson")

    def test_select_by_age(self):
        self._create_test_data()
        records = self.table.select_record(age=20)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][3], 20)

    def test_select_by_sex(self):
        self._create_test_data()
        records = self.table.select_record(sex="F")
        self.assertEqual(len(records), 2)

    def test_select_by_multiple_filters(self):
        self._create_test_data()
        records = self.table.select_record(
            first_name="John",
            second_name="Doe",
            age=20,
            sex="M"
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], (1, "John", "Doe", 20, "M"))

    def test_select_no_results(self):
        """Выборка без результатов."""
        self._create_test_data()
        records = self.table.select_record(student_id=999)
        self.assertEqual(len(records), 0)

    def test_select_case_sensitive(self):
        """Поиск чувствителен к регистру."""
        self._create_test_data()
        records = self.table.select_record(first_name="john")
        self.assertEqual(len(records), 0)

    def test_select_all_filters_none(self):
        """Все фильтры None - возвращает все записи."""
        self._create_test_data()
        records = self.table.select_record(None, None, None, None, None)
        self.assertEqual(len(records), 5)

    # update_record

    def test_update_record_all_fields(self):
        self._create_test_data()
        updated = self.table.update_record(
            1,
            first_name="Johnny",
            second_name="Doe-Smith",
            age=25,
            sex="M"
        )
        self.assertEqual(updated, (1, "Johnny", "Doe-Smith", 25, "M"))

    def test_update_record_partial(self):
        """Обновление только некоторых полей."""
        self._create_test_data()
        updated = self.table.update_record(1, age=25)
        self.assertEqual(updated[3], 25)
        self.assertEqual(updated[1], "John")

    def test_update_record_only_name(self):
        self._create_test_data()
        updated = self.table.update_record(2, first_name="Janet")
        self.assertEqual(updated[1], "Janet")
        self.assertEqual(updated[2], "Smith")

    def test_update_record_only_second_name(self):
        self._create_test_data()
        updated = self.table.update_record(1, second_name="Doe-Smith")
        self.assertEqual(updated[2], "Doe-Smith")

    def test_update_record_only_sex(self):
        self._create_test_data()
        updated = self.table.update_record(2, sex="M")
        self.assertEqual(updated[4], "M")

    def test_update_record_not_found(self):
        self._create_test_data()
        with self.assertRaises(StudentNotFoundError) as ctx:
            self.table.update_record(999, first_name="Test")
        self.assertIn("Запись с id=999 не найдена", str(ctx.exception))

    def test_update_record_negative_age(self):
        self._create_test_data()
        with self.assertRaises(InvalidAgeError) as ctx:
            self.table.update_record(1, age=-10)
        self.assertIn("Некорректный возраст: -10", str(ctx.exception))

    def test_update_record_strips_spaces(self):
        self._create_test_data()
        updated = self.table.update_record(
            1,
            first_name="  Johnny  ",
            second_name="  Doe-Smith  "
        )
        self.assertEqual(updated[1], "Johnny")
        self.assertEqual(updated[2], "Doe-Smith")

    def test_update_record_same_values(self):
        self._create_test_data()
        current = self.table.select_record(student_id=1)[0]
        updated = self.table.update_record(
            1,
            first_name=current[1],
            second_name=current[2],
            age=current[3],
            sex=current[4]
        )
        self.assertEqual(updated, current)

    def test_update_record_empty_name(self):
        self._create_test_data()
        updated = self.table.update_record(1, first_name="", second_name="")
        self.assertEqual(updated[1], "")
        self.assertEqual(updated[2], "")

    # delete_record

    def test_delete_by_id_success(self):
        self._create_test_data()
        deleted = self.table.delete_record(student_id=1)
        self.assertEqual(len(deleted), 1)
        self.assertEqual(deleted[0][0], 1)
        self.assertEqual(self.table.count(), 4)

    def test_delete_by_id_not_found(self):
        self._create_test_data()
        deleted = self.table.delete_record(student_id=999)
        self.assertEqual(len(deleted), 0)
        self.assertEqual(self.table.count(), 5)

    def test_delete_by_first_name(self):
        self._create_test_data()
        deleted = self.table.delete_record(first_name="Jane")
        self.assertEqual(len(deleted), 1)
        self.assertEqual(deleted[0][1], "Jane")
        self.assertEqual(self.table.count(), 4)

    def test_delete_by_second_name(self):
        self._create_test_data()
        deleted = self.table.delete_record(second_name="Johnson")
        self.assertEqual(len(deleted), 1)
        self.assertEqual(deleted[0][2], "Johnson")

    def test_delete_by_age(self):
        self._create_test_data()
        deleted = self.table.delete_record(age=20)
        self.assertEqual(len(deleted), 1)

    def test_delete_by_sex(self):
        self._create_test_data()
        deleted = self.table.delete_record(sex="F")
        self.assertEqual(len(deleted), 2)

    def test_delete_by_multiple_filters(self):
        self._create_test_data()
        deleted = self.table.delete_record(
            first_name="John",
            second_name="Doe",
            age=20
        )
        self.assertEqual(len(deleted), 1)
        self.assertEqual(deleted[0], (1, "John", "Doe", 20, "M"))

    def test_delete_all_records(self):
        self._create_test_data()
        deleted = self.table.delete_record()
        self.assertEqual(len(deleted), 5)
        self.assertEqual(self.table.count(), 0)

    def test_delete_no_matching_records(self):
        """Удаление по фильтру без совпадений."""
        self._create_test_data()
        deleted = self.table.delete_record(first_name="Nonexistent")
        self.assertEqual(len(deleted), 0)

    def test_delete_by_age_multiple_matches(self):
        """Удаление по возрасту с несколькими совпадениями."""
        self._create_test_data()
        self.table.create_record(6, "Test", "User", 20, "M")
        deleted = self.table.delete_record(age=20)
        self.assertEqual(len(deleted), 2)

    def test_delete_empty_table(self):
        """Удаление из пустой таблицы."""
        deleted = self.table.delete_record()
        self.assertEqual(deleted, [])
        self.assertEqual(self.table.count(), 0)

    def test_delete_by_id_empty_table(self):
        deleted = self.table.delete_record(student_id=1)
        self.assertEqual(deleted, [])
        self.assertEqual(self.table.count(), 0)



    def test_count(self):
        """Метод count возвращает правильное количество."""
        self.assertEqual(self.table.count(), 0)
        self._create_test_data()
        self.assertEqual(self.table.count(), 5)

    def test_clear(self):
        """Метод clear очищает таблицу."""
        self._create_test_data()
        self.assertEqual(self.table.count(), 5)
        self.table.clear()
        self.assertEqual(self.table.count(), 0)

    def test_clear_empty_table(self):
        """Очистка пустой таблицы."""
        self.table.clear()
        self.assertEqual(self.table.count(), 0)


if __name__ == "__main__":
    unittest.main()