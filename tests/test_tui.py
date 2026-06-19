import unittest
from unittest.mock import patch
from io import StringIO
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.db.tui import StudentTUI, run


class TestStudentTUI(unittest.TestCase):

    def setUp(self):
        """Создание экземпляра TUI перед каждым тестом."""
        self.tui = StudentTUI()

    def tearDown(self):
        """Очистка таблицы после каждого теста."""
        self.tui.db.clear()

    def test_print_menu(self):
        with patch('sys.stdout', new_callable=StringIO) as captured:
            self.tui._print_menu()
            output = captured.getvalue()
            self.assertIn("=== База студентов ===", output)
            self.assertIn("1. Добавить запись", output)
            self.assertIn("0. Выход", output)

    def test_read_int_valid(self):
        with patch('builtins.input', return_value='42'):
            self.assertEqual(self.tui._read_int(""), 42)

    def test_read_int_invalid_then_valid(self):
        with patch('builtins.input', side_effect=['abc', '123']):
            with patch('sys.stdout', new_callable=StringIO) as captured:
                self.assertEqual(self.tui._read_int(""), 123)
                self.assertIn("Ошибка: введите целое число", captured.getvalue())

    def test_read_optional_int_valid(self):
        with patch('builtins.input', return_value='25'):
            self.assertEqual(self.tui._read_optional_int(""), 25)

    def test_read_optional_int_empty(self):
        with patch('builtins.input', return_value=''):
            self.assertIsNone(self.tui._read_optional_int(""))

    def test_print_records_with_data(self):
        records = [(1, "John", "Doe", 20, "M")]
        with patch('sys.stdout', new_callable=StringIO) as captured:
            self.tui._print_records(records)
            self.assertIn("John", captured.getvalue())

    def test_print_records_empty(self):
        with patch('sys.stdout', new_callable=StringIO) as captured:
            self.tui._print_records([])
            self.assertIn("Записи не найдены", captured.getvalue())

    @patch('builtins.input')
    @patch('src.db.tui.StudentTUI._read_int')
    def test_add_student_success(self, mock_read_int, mock_input):
        """Успешное добавление студента."""
        mock_read_int.side_effect = [1, 20]
        mock_input.side_effect = ["John", "Doe", "M"]

        with patch('sys.stdout', new_callable=StringIO) as captured:
            self.tui._add_student()
            self.assertIn("Запись добавлена", captured.getvalue())
            self.assertEqual(self.tui.db.count(), 1)

    @patch('builtins.input')
    @patch('src.db.tui.StudentTUI._read_int')
    def test_add_student_duplicate(self, mock_read_int, mock_input):
        """Добавление дубликата."""
        self.tui.db.create_record(1, "John", "Doe", 20, "M")
        mock_read_int.side_effect = [1, 20]
        mock_input.side_effect = ["Jane", "Smith", "F"]

        with patch('sys.stdout', new_callable=StringIO) as captured:
            self.tui._add_student()
            self.assertIn("Запись с id=1 уже существует", captured.getvalue())

    @patch('builtins.input')
    @patch('src.db.tui.StudentTUI._read_int')
    def test_add_student_invalid_age(self, mock_read_int, mock_input):
        """Добавление с отрицательным возрастом."""
        mock_read_int.side_effect = [1, -5]
        mock_input.side_effect = ["John", "Doe", "M"]

        with patch('sys.stdout', new_callable=StringIO) as captured:
            self.tui._add_student()
            self.assertIn("Некорректный возраст", captured.getvalue())

    def test_show_all_empty(self):
        """Показ пустой таблицы."""
        with patch('sys.stdout', new_callable=StringIO) as captured:
            self.tui._show_all_students()
            self.assertIn("Записи не найдены", captured.getvalue())

    def test_show_all_with_data(self):
        """Показ с данными."""
        self.tui.db.create_record(1, "John", "Doe", 20, "M")
        with patch('sys.stdout', new_callable=StringIO) as captured:
            self.tui._show_all_students()
            self.assertIn("John", captured.getvalue())

    @patch('builtins.input')
    @patch('src.db.tui.StudentTUI._read_optional_int')
    def test_find_by_id(self, mock_read_optional, mock_input):
        """Поиск по ID."""
        self.tui.db.create_record(1, "John", "Doe", 20, "M")
        mock_read_optional.side_effect = [1, None]
        mock_input.side_effect = ["", "", ""]

        with patch('sys.stdout', new_callable=StringIO) as captured:
            self.tui._find_students_by_filter()
            self.assertIn("John", captured.getvalue())

    @patch('builtins.input')
    @patch('src.db.tui.StudentTUI._read_optional_int')
    def test_find_no_results(self, mock_read_optional, mock_input):
        """Поиск без результатов."""
        mock_read_optional.side_effect = [999, None]
        mock_input.side_effect = ["", "", ""]

        with patch('sys.stdout', new_callable=StringIO) as captured:
            self.tui._find_students_by_filter()
            self.assertIn("Записи не найдены", captured.getvalue())


    @patch('builtins.input')
    @patch('src.db.tui.StudentTUI._read_optional_int')
    def test_update_no_criteria(self, mock_read_optional, mock_input):
        """Обновление без критериев."""
        mock_read_optional.return_value = None
        mock_input.return_value = ""

        with patch('sys.stdout', new_callable=StringIO) as captured:
            self.tui._update_students_by_filter()
            self.assertIn("нужно указать хотя бы один критерий", captured.getvalue())

    @patch('builtins.input')
    @patch('src.db.tui.StudentTUI._read_optional_int')
    def test_update_cancel(self, mock_read_optional, mock_input):
        """Отмена обновления."""
        self.tui.db.create_record(1, "John", "Doe", 20, "M")
        mock_read_optional.side_effect = [None, None]
        mock_input.side_effect = ["John", "", "", "н"]

        with patch('sys.stdout', new_callable=StringIO) as captured:
            self.tui._update_students_by_filter()
            self.assertIn("Обновление отменено", captured.getvalue())

    @patch('builtins.input')
    @patch('src.db.tui.StudentTUI._read_optional_int')
    def test_update_success(self, mock_read_optional, mock_input):
        """Успешное обновление."""
        self.tui.db.create_record(1, "John", "Doe", 20, "M")
        mock_read_optional.side_effect = [None, None, 25]
        mock_input.side_effect = ["John", "", "", "д", "", "", ""]

        with patch('sys.stdout', new_callable=StringIO) as captured:
            self.tui._update_students_by_filter()
            self.assertIn("Обновленные записи", captured.getvalue())

    @patch('builtins.input')
    @patch('src.db.tui.StudentTUI._read_optional_int')
    def test_delete_no_criteria(self, mock_read_optional, mock_input):
        """Удаление без критериев."""
        mock_read_optional.return_value = None
        mock_input.return_value = ""

        with patch('sys.stdout', new_callable=StringIO) as captured:
            self.tui._delete_students_by_filter()
            self.assertIn("укажите критерий для поиска", captured.getvalue())

    @patch('builtins.input')
    @patch('src.db.tui.StudentTUI._read_optional_int')
    def test_delete_cancel(self, mock_read_optional, mock_input):
        """Отмена удаления."""
        self.tui.db.create_record(1, "John", "Doe", 20, "M")
        mock_read_optional.return_value = None
        mock_input.side_effect = ["John", "", "", "н"]

        with patch('sys.stdout', new_callable=StringIO):
            self.tui._delete_students_by_filter()

        self.assertEqual(self.tui.db.count(), 1)

    @patch('builtins.input')
    @patch('src.db.tui.StudentTUI._read_optional_int')
    def test_delete_success(self, mock_read_optional, mock_input):
        """Успешное удаление."""
        self.tui.db.create_record(1, "John", "Doe", 20, "M")
        mock_read_optional.return_value = None
        mock_input.side_effect = ["John", "", "", "д"]

        with patch('sys.stdout', new_callable=StringIO) as captured:
            self.tui._delete_students_by_filter()
            self.assertIn("Удаленные записи", captured.getvalue())

        self.assertEqual(self.tui.db.count(), 0)

    @patch('builtins.input')
    def test_run_exit(self, mock_input):
        """Выход из программы."""
        mock_input.side_effect = ["0"]

        with patch('sys.stdout', new_callable=StringIO) as captured:
            with patch('src.db.tui.StudentTUI._print_menu'):
                self.tui.run()
                self.assertIn("Выход из программы", captured.getvalue())

    @patch('builtins.input')
    def test_run_invalid_command(self, mock_input):
        """Неверная команда."""
        mock_input.side_effect = ["999", "0"]

        with patch('sys.stdout', new_callable=StringIO) as captured:
            with patch('src.db.tui.StudentTUI._print_menu'):
                self.tui.run()
                self.assertIn("Неизвестная команда", captured.getvalue())

    @patch('builtins.input')
    def test_run_add_command(self, mock_input):
        """Выбор добавления."""
        mock_input.side_effect = ["1", "0"]

        with patch.object(self.tui, '_add_student') as mock_add:
            with patch('sys.stdout', new_callable=StringIO):
                with patch('src.db.tui.StudentTUI._print_menu'):
                    self.tui.run()
                    mock_add.assert_called_once()

    @patch('builtins.input')
    def test_global_run_function(self, mock_input):
        """Тест глобальной функции run()."""
        mock_input.side_effect = ["0"]

        with patch('sys.stdout', new_callable=StringIO) as captured:
            with patch('src.db.tui.StudentTUI._print_menu'):
                run()
                self.assertIn("Добро пожаловать в базу студентов", captured.getvalue())
                self.assertIn("Выход из программы", captured.getvalue())


if __name__ == "__main__":
    unittest.main()