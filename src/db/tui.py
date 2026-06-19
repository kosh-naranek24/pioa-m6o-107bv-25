# src/db/tui.py
from src.db.backend.file import FileDatabase
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import (
    TableNotFoundError,
    TableAlreadyExistsError,
    MissingColumnError,
    UnknownColumnError,
    InvalidStorageDataError,
)


class TUI:
    """Текстовый пользовательский интерфейс."""

    def __init__(self) -> None:
        print("\n=== Выбор типа базы данных ===")
        print("1. In-memory (данные не сохраняются)")
        print("2. File-based (данные сохраняются в файл)")

        while True:
            choice = input("Выберите тип (1/2): ").strip()
            if choice == "1":
                self.database = MemoryDatabase()
                print("Выбран in-memory режим.")
                break
            elif choice == "2":
                self.database = FileDatabase()
                print("Выбран файловый режим. Данные хранятся в папке 'data/'")
                break
            else:
                print("Неверный выбор. Попробуйте снова.")

        self.current_table = "students"
        self._init_students_table()
        self.run()

    def _init_students_table(self) -> None:
        """Инициализация таблицы students."""
        try:
            self.database.create_table(
                "students",
                ("student_id", "first_name", "second_name", "age", "sex")
            )
        except TableAlreadyExistsError:
            pass  # Таблица уже существует

    def _print_menu(self) -> None:
        """Вывод меню."""
        print("\n=== База студентов ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи по фильтру")
        print("4. Обновить записи по фильтру")
        print("5. Удалить записи по фильтру")
        print("0. Выход")

    def _read_int(self, prompt: str) -> int:
        """Чтение целого числа."""
        while True:
            raw = input(prompt).strip()
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число.")

    def _read_optional_int(self, prompt: str) -> int | None:
        """Чтение опционального целого числа."""
        while True:
            raw = input(prompt).strip()
            if raw == "":
                return None
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте поле пустым.")

    def _print_records(self, records: list[dict]) -> None:
        """Вывод записей."""
        if not records:
            print("Записи не найдены.")
            return

        for record in records:
            print(f"({record['student_id']}, '{record['first_name']}', "
                  f"'{record['second_name']}', {record['age']}, '{record['sex']}')")

    def _add_student(self) -> None:
        """Добавление студента."""
        print("\nДобавление записи")

        student_id = self._read_int("ID: ")
        first_name = input("Имя: ").strip()
        second_name = input("Фамилия: ").strip()
        age = self._read_int("Возраст: ")
        sex = input("Пол (М/Ж): ").strip()

        try:
            record = {
                "student_id": student_id,
                "first_name": first_name,
                "second_name": second_name,
                "age": age,
                "sex": sex,
            }
            self.database.insert_record(self.current_table, record)
            print(f"Запись добавлена: {record}")

        except (MissingColumnError, UnknownColumnError) as e:
            print(f"Ошибка: {e}")
        except TableNotFoundError as e:
            print(f"Ошибка: {e}. Сначала создайте таблицу.")

    def _show_all_students(self) -> None:
        """Показать всех студентов."""
        print("\nСписок записей")
        try:
            records = self.database.select_records(self.current_table)
            self._print_records(records)
        except TableNotFoundError as e:
            print(f"Ошибка: {e}")

    def _find_students_by_filter(self) -> None:
        """Поиск студентов по фильтру."""
        print("\nПоиск по фильтру (Enter = пропустить поле)")

        student_id = self._read_optional_int("ID: ")
        first_name = input("Имя: ").strip() or None
        second_name = input("Фамилия: ").strip() or None
        age = self._read_optional_int("Возраст: ")
        sex = input("Пол (М/Ж): ").strip() or None

        filters = {}
        if student_id is not None:
            filters["student_id"] = student_id
        if first_name is not None:
            filters["first_name"] = first_name
        if second_name is not None:
            filters["second_name"] = second_name
        if age is not None:
            filters["age"] = age
        if sex is not None:
            filters["sex"] = sex

        try:
            records = self.database.select_records(self.current_table, **filters)
            self._print_records(records)
        except (TableNotFoundError, UnknownColumnError) as e:
            print(f"Ошибка: {e}")

    def _update_students_by_filter(self) -> None:
        """Обновление студентов по фильтру."""
        print("\nОбновление записей")
        print("(Enter = пропустить поле)")

        # Критерии поиска
        student_id = self._read_optional_int("ID (критерий): ")
        first_name = input("Имя (критерий): ").strip() or None
        second_name = input("Фамилия (критерий): ").strip() or None
        age = self._read_optional_int("Возраст (критерий): ")
        sex = input("Пол (критерий): ").strip() or None

        filters = {}
        if student_id is not None:
            filters["student_id"] = student_id
        if first_name is not None:
            filters["first_name"] = first_name
        if second_name is not None:
            filters["second_name"] = second_name
        if age is not None:
            filters["age"] = age
        if sex is not None:
            filters["sex"] = sex

        if not filters:
            print("Ошибка: нужно указать хотя бы один критерий для поиска.")
            return

        try:
            # Находим записи для обновления
            to_update = self.database.select_records(self.current_table, **filters)

            if not to_update:
                print("Записи не найдены.")
                return

            print(f"\nНайдено записей для обновления: {len(to_update)}")
            self._print_records(to_update)

            confirm = input("\nПродолжить обновление? (д/н): ").strip().lower()
            if confirm != 'д':
                print("Обновление отменено.")
                return

            # Новые значения
            print("\n--- Новые значения ---")
            print("(Оставьте поле пустым, если не хотите его менять)")

            updates = {}
            new_first_name = input("Новое имя (Enter - не менять): ").strip()
            if new_first_name:
                updates["first_name"] = new_first_name

            new_second_name = input("Новая фамилия (Enter - не менять): ").strip()
            if new_second_name:
                updates["second_name"] = new_second_name

            new_age = self._read_optional_int("Новый возраст (Enter - не менять): ")
            if new_age is not None:
                updates["age"] = new_age

            new_sex = input("Новый пол (М/Ж, Enter - не менять): ").strip()
            if new_sex:
                updates["sex"] = new_sex

            if not updates:
                print("Ошибка: нужно указать хотя бы одно поле для обновления.")
                return

            # Обновляем записи
            table = self.database._load_table(self.current_table)
            updated_records = []
            for record in to_update:
                for key, value in updates.items():
                    if key in record:
                        record[key] = value
                updated_records.append(record)
            self.database._save_table(self.current_table, table)

            print("\nОбновленные записи:")
            self._print_records(updated_records)

        except (TableNotFoundError, UnknownColumnError) as e:
            print(f"Ошибка: {e}")

    def _delete_students_by_filter(self) -> None:
        """Удаление студентов по фильтру."""
        print("\nУдаление записей")
        print("(Enter = пропустить поле)")

        student_id = self._read_optional_int("ID: ")
        first_name = input("Имя: ").strip() or None
        second_name = input("Фамилия: ").strip() or None
        age = self._read_optional_int("Возраст: ")
        sex = input("Пол (М/Ж): ").strip() or None

        filters = {}
        if student_id is not None:
            filters["student_id"] = student_id
        if first_name is not None:
            filters["first_name"] = first_name
        if second_name is not None:
            filters["second_name"] = second_name
        if age is not None:
            filters["age"] = age
        if sex is not None:
            filters["sex"] = sex

        if not filters:
            print("Ошибка: укажите критерий для поиска.")
            return

        try:
            # Находим записи для удаления
            to_delete = self.database.select_records(self.current_table, **filters)

            if not to_delete:
                print("Записи не найдены.")
                return

            print(f"\nНайдено записей для удаления: {len(to_delete)}")
            self._print_records(to_delete)

            confirm = input("\nПодтвердите удаление (д/н): ").strip().lower()
            if confirm != 'д':
                print("Удаление отменено.")
                return

            # Удаляем записи
            table = self.database._load_table(self.current_table)
            table.records = [
                r for r in table.records
                if not all(r.get(k) == v for k, v in filters.items())
            ]
            self.database._save_table(self.current_table, table)

            print(f"\n✅ Удалено записей: {len(to_delete)}")
            self._print_records(to_delete)

        except (TableNotFoundError, UnknownColumnError) as e:
            print(f"Ошибка: {e}")

    def run(self) -> None:
        """Запуск основного цикла."""
        while True:
            self._print_menu()
            action = input("Выберите действие: ").strip()

            if action == "1":
                self._add_student()
            elif action == "2":
                self._show_all_students()
            elif action == "3":
                self._find_students_by_filter()
            elif action == "4":
                self._update_students_by_filter()
            elif action == "5":
                self._delete_students_by_filter()
            elif action == "0":
                print("Выход из программы.")
                break
            else:
                print("Неизвестная команда. Повторите ввод.")


def run() -> None:
    """Точка входа для TUI."""
    app = TUI()


if __name__ == "__main__":
    run()

StudentTUI = TUI