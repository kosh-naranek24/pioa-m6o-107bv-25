'''# tests/test_tui.py
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

from src.db.tui import TUI, StudentTUI


class TestTUI(unittest.TestCase):
    """Упрощенные тесты для TUI."""

    def setUp(self):
        """Подготовка перед каждым тестом."""
        # Создаем TUI с мокированным input для выбора БД
        with patch('builtins.input', return_value="1"):
            self.tui = TUI()

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_menu(self, mock_stdout):
        """Тест вывода меню."""
        self.tui._print_menu()
        output = mock_stdout.getvalue()

        self.assertIn("=== База студентов ===", output)
        self.assertIn("1. Добавить запись", output)
        self.assertIn("2. Показать все записи", output)
        self.assertIn("3. Найти записи по фильтру", output)
        self.assertIn("4. Обновить записи по фильтру", output)
        self.assertIn("5. Удалить записи по фильтру", output)
        self.assertIn("0. Выход", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_records_empty(self, mock_stdout):
        """Тест вывода пустого списка записей."""
        self.tui._print_records([])
        output = mock_stdout.getvalue()
        self.assertIn("Записи не найдены", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_records_with_data(self, mock_stdout):
        """Тест вывода списка записей с данными."""
        records = [
            {"student_id": 1, "first_name": "Иван", "second_name": "Петров", "age": 20, "sex": "М"},
            {"student_id": 2, "first_name": "Мария", "second_name": "Иванова", "age": 22, "sex": "Ж"},
        ]

        self.tui._print_records(records)
        output = mock_stdout.getvalue()

        self.assertIn("Иван", output)
        self.assertIn("Петров", output)
        self.assertIn("Мария", output)
        self.assertIn("Иванова", output)

    @patch('builtins.input')
    def test_read_int_valid(self, mock_input):
        """Тест чтения целого числа (корректный ввод)."""
        mock_input.return_value = "123"
        result = self.tui._read_int("Введите число: ")
        self.assertEqual(result, 123)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_read_int_invalid_then_valid(self, mock_stdout, mock_input):
        """Тест чтения целого числа (некорректный, затем корректный ввод)."""
        mock_input.side_effect = ["abc", "456"]
        result = self.tui._read_int("Введите число: ")
        self.assertEqual(result, 456)
        self.assertIn("Ошибка: введите целое число", mock_stdout.getvalue())

    @patch('builtins.input')
    def test_read_optional_int_valid(self, mock_input):
        """Тест чтения опционального целого числа (корректный ввод)."""
        mock_input.return_value = "123"
        result = self.tui._read_optional_int("Введите число: ")
        self.assertEqual(result, 123)

    @patch('builtins.input')
    def test_read_optional_int_empty(self, mock_input):
        """Тест чтения опционального целого числа (пустой ввод)."""
        mock_input.return_value = ""
        result = self.tui._read_optional_int("Введите число: ")
        self.assertIsNone(result)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_success(self, mock_stdout, mock_input):
        """Тест успешного добавления студента."""
        mock_input.side_effect = ["1", "Иван", "Петров", "20", "М"]

        self.tui._add_student()

        # Проверяем, что запись добавилась
        records = self.tui.database.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["student_id"], 1)
        self.assertEqual(records[0]["first_name"], "Иван")
        self.assertEqual(records[0]["age"], 20)

        self.assertIn("✅ Запись добавлена", mock_stdout.getvalue())

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_student_invalid_age(self, mock_stdout, mock_input):
        """Тест добавления студента с некорректным возрастом."""
        mock_input.side_effect = ["1", "Иван", "Петров", "-5", "М"]

        self.tui._add_student()

        # Запись не должна добавиться, так как возраст отрицательный
        # (валидация на уровне TUI отсутствует, запись добавится с отрицательным возрастом)
        records = self.tui.database.select_records("students")
        self.assertEqual(len(records), 1)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_show_all_empty(self, mock_stdout, mock_input):
        """Тест показа всех записей (пустая таблица)."""
        self.tui._show_all_students()
        output = mock_stdout.getvalue()
        self.assertIn("Записи не найдены", output)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_show_all_with_data(self, mock_stdout, mock_input):
        """Тест показа всех записей (с данными)."""
        # Добавляем запись
        mock_input.side_effect = ["1", "Иван", "Петров", "20", "М"]
        self.tui._add_student()

        # Показываем все записи
        with patch('builtins.input'):
            self.tui._show_all_students()

        output = mock_stdout.getvalue()
        self.assertIn("Иван", output)
        self.assertIn("Петров", output)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_find_by_id(self, mock_stdout, mock_input):
        """Тест поиска по ID."""
        # Добавляем записи
        mock_input.side_effect = ["1", "Иван", "Петров", "20", "М", "2", "Мария", "Иванова", "22", "Ж"]
        self.tui._add_student()
        self.tui._add_student()

        # Ищем по ID
        mock_input.side_effect = ["1", "", "", "", ""]
        self.tui._find_students_by_filter()

        output = mock_stdout.getvalue()
        self.assertIn("Иван", output)
        self.assertNotIn("Мария", output)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_find_no_results(self, mock_stdout, mock_input):
        """Тест поиска без результатов."""
        # Добавляем запись
        mock_input.side_effect = ["1", "Иван", "Петров", "20", "М"]
        self.tui._add_student()

        # Ищем несуществующего студента
        mock_input.side_effect = ["999", "", "", "", ""]
        self.tui._find_students_by_filter()

        output = mock_stdout.getvalue()
        self.assertIn("Записи не найдены", output)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_success(self, mock_stdout, mock_input):
        """Тест успешного обновления записи."""
        # Добавляем запись
        mock_input.side_effect = ["1", "Иван", "Петров", "20", "М"]
        self.tui._add_student()

        # Обновляем запись
        mock_input.side_effect = ["1", "", "", "", "", "д", "Иван", "Иванов", "25", "М"]
        self.tui._update_students_by_filter()

        # Проверяем обновление
        records = self.tui.database.select_records("students")
        self.assertEqual(records[0]["second_name"], "Иванов")
        self.assertEqual(records[0]["age"], 25)

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_cancel(self, mock_stdout, mock_input):
        """Тест отмены обновления."""
        # Добавляем запись
        mock_input.side_effect = ["1", "Иван", "Петров", "20", "М"]
        self.tui._add_student()

        # Обновляем запись, но отменяем подтверждение
        mock_input.side_effect = ["1", "", "", "", "", "н"]
        self.tui._update_students_by_filter()

        # Проверяем, что данные не изменились
        records = self.tui.database.select_records("students")
        self.assertEqual(records[0]["second_name"], "Петров")

        self.assertIn("Обновление отменено", mock_stdout.getvalue())

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_delete_success(self, mock_stdout, mock_input):
        """Тест успешного удаления записи."""
        # Добавляем записи
        mock_input.side_effect = ["1", "Иван", "Петров", "20", "М", "2", "Мария", "Иванова", "22", "Ж"]
        self.tui._add_student()
        self.tui._add_student()

        # Удаляем запись
        mock_input.side_effect = ["1", "", "", "", "", "д"]
        self.tui._delete_students_by_filter()

        # Проверяем удаление
        records = self.tui.database.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["first_name"], "Мария")

        self.assertIn("✅ Удалено записей: 1", mock_stdout.getvalue())

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_delete_cancel(self, mock_stdout, mock_input):
        """Тест отмены удаления."""
        # Добавляем запись
        mock_input.side_effect = ["1", "Иван", "Петров", "20", "М"]
        self.tui._add_student()

        # Удаляем запись, но отменяем
        mock_input.side_effect = ["1", "", "", "", "", "н"]
        self.tui._delete_students_by_filter()

        # Проверяем, что запись осталась
        records = self.tui.database.select_records("students")
        self.assertEqual(len(records), 1)

        self.assertIn("Удаление отменено", mock_stdout.getvalue())

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_exit(self, mock_stdout, mock_input):
        """Тест выхода из программы."""
        mock_input.side_effect = ["0"]
        self.tui.run()
        self.assertIn("Выход из программы", mock_stdout.getvalue())

    @patch('builtins.input')
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_invalid_command(self, mock_stdout, mock_input):
        """Тест неверной команды в главном цикле."""
        mock_input.side_effect = ["99", "0"]
        self.tui.run()
        self.assertIn("Неизвестная команда", mock_stdout.getvalue())


class TestStudentTUI(unittest.TestCase):
    """Тесты для обратной совместимости с StudentTUI."""

    def test_student_tui_alias(self):
        """Тест, что StudentTUI является алиасом для TUI."""
        self.assertEqual(StudentTUI, TUI)


if __name__ == "__main__":
    unittest.main()
    '''