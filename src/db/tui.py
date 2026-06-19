from .backend.memory import StudentTable
from .backend.errors import DuplicateIDError, InvalidAgeError, StudentNotFoundError


class StudentTUI:


    def __init__(self) -> None:
        """Инициализация интерфейса с новой таблицей."""
        self.db = StudentTable()

    def _print_menu(self) -> None:
        """Вывод текстового меню в консоль."""
        print("\n=== База студентов ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи по фильтру")
        print("4. Обновить записи по фильтру")
        print("5. Удалить записи по фильтру")
        print("0. Выход")

    @staticmethod
    def _read_int(prompt: str) -> int:
        """Чтение целочисленного значения из консоли."""
        while True:
            raw = input(prompt).strip()
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число.")

    @staticmethod
    def _read_optional_int(prompt: str) -> int | None:
        """Чтение необязательного целочисленного значения."""
        while True:
            raw = input(prompt).strip()
            if raw == "":
                return None
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте поле пустым.")

    @staticmethod
    def _print_records(records: list[tuple[int, str, str, int, str]]) -> None:
        """Вывод списка записей."""
        if not records:
            print("Записи не найдены.")
            return
        for record in records:
            print(f"  {record}")
        print(f"\nВсего записей: {len(records)}")

    def _add_student(self) -> None:
        """Добавление новой записи в базу данных."""
        print("\nДобавление записи")

        student_id = self._read_int("ID: ")
        first_name = input("Имя: ").strip()
        second_name = input("Фамилия: ").strip()
        age = self._read_int("Возраст: ")
        sex = input("Пол (М/Ж): ").strip()

        try:
            record = self.db.create_record(student_id, first_name, second_name, age, sex)
            print(f"Запись добавлена: {record}")
        except (DuplicateIDError, InvalidAgeError) as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")

    def _show_all_students(self) -> None:
        """Вывод всех записей из базы данных."""
        print("\n=== Список всех записей ===")
        records = self.db.select_record()
        self._print_records(records)

    def _find_students_by_filter(self) -> None:
        """Поиск записей по заданным фильтрам."""
        print("\n=== Поиск по фильтру ===")
        print("(Enter = пропустить поле)")

        student_id = self._read_optional_int("ID: ")
        first_name = input("Имя: ").strip() or None
        second_name = input("Фамилия: ").strip() or None
        age = self._read_optional_int("Возраст: ")
        sex = input("Пол (М/Ж): ").strip() or None

        records = self.db.select_record(
            student_id=student_id,
            first_name=first_name,
            second_name=second_name,
            age=age,
            sex=sex,
        )

        self._print_records(records)

    def _update_students_by_filter(self) -> None:
        """Обновление записей по фильтру."""
        print("\n=== Обновление записей по фильтру ===")
        print("(Enter = пропустить поле)")

        # Критерии поиска
        student_id = self._read_optional_int("ID (критерий): ")
        first_name = input("Имя (критерий): ").strip() or None
        second_name = input("Фамилия (критерий): ").strip() or None
        age = self._read_optional_int("Возраст (критерий): ")
        sex = input("Пол (критерий): ").strip() or None

        # Проверка наличия критериев
        if all(p is None for p in [student_id, first_name, second_name, age, sex]):
            print("Ошибка: нужно указать хотя бы один критерий для поиска.")
            return

        # Поиск записей для обновления
        to_update = self.db.select_record(
            student_id=student_id,
            first_name=first_name,
            second_name=second_name,
            age=age,
            sex=sex
        )

        if not to_update:
            print("Записи, соответствующие критериям, не найдены.")
            return

        print(f"\nНайдено записей для обновления: {len(to_update)}")
        print("\nЗаписи, которые будут обновлены:")
        for record in to_update:
            print(f"  {record}")

        confirm = input("\nПродолжить обновление? (д/н): ").strip().lower()
        if confirm != 'д':
            print("Обновление отменено.")
            return

        # Новые значения
        print("\n--- Новые значения ---")
        print("(Оставьте поле пустым, если не хотите его менять)")

        new_first_name = input("Новое имя (Enter - не менять): ").strip() or None
        new_second_name = input("Новая фамилия (Enter - не менять): ").strip() or None
        new_age = self._read_optional_int("Новый возраст (Enter - не менять): ")
        new_sex = input("Новый пол (М/Ж, Enter - не менять): ").strip() or None

        if all(p is None for p in [new_first_name, new_second_name, new_age, new_sex]):
            print("Ошибка: нужно указать хотя бы одно поле для обновления.")
            return

        try:
            updated = []
            for record in to_update:
                result = self.db.update_record(
                    student_id=record[0],
                    first_name=new_first_name,
                    second_name=new_second_name,
                    age=new_age,
                    sex=new_sex
                )
                if result:
                    updated.append(result)

            if updated:
                print("\nОбновленные записи:")
                for record in updated:
                    print(f"  {record}")
            else:
                print("Ни одна запись не была обновлена.")

        except (StudentNotFoundError, InvalidAgeError) as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")

    def _delete_students_by_filter(self) -> None:
        """Удаление записей по фильтру."""
        print("\n=== Удаление записей по фильтру ===")
        print("(Enter = пропустить поле)")

        student_id = self._read_optional_int("ID: ")
        first_name = input("Имя: ").strip() or None
        second_name = input("Фамилия: ").strip() or None
        age = self._read_optional_int("Возраст: ")
        sex = input("Пол (М/Ж): ").strip() or None

        # Проверка наличия критериев
        if all(p is None for p in [student_id, first_name, second_name, age, sex]):
            print("Ошибка: укажите критерий для поиска.")
            return

        # Поиск записей для удаления
        to_delete = self.db.select_record(
            student_id=student_id,
            first_name=first_name,
            second_name=second_name,
            age=age,
            sex=sex
        )

        if not to_delete:
            print("Записи, соответствующие критериям, не найдены.")
            return

        print(f"\nНайдено записей для удаления: {len(to_delete)}")
        print("\nЗаписи, которые будут удалены:")
        for i, record in enumerate(to_delete, 1):
            print(f"  {i}. ID: {record[0]}, {record[1]} {record[2]}, {record[3]} лет, {record[4]}")

        confirm = input("\nПодтвердите удаление (д/н): ").strip().lower()
        if confirm != 'д':
            print("Удаление отменено.")
            return

        try:
            deleted = self.db.delete_record(
                student_id=student_id,
                first_name=first_name,
                second_name=second_name,
                age=age,
                sex=sex
            )

            if deleted:
                print(f"\nУдаленные записи ({len(deleted)} шт.):")
                for i, record in enumerate(deleted, 1):
                    print(f"  {i}. ID: {record[0]}, {record[1]} {record[2]}, {record[3]} лет, {record[4]}")
            else:
                print("Ни одна запись не была удалена.")

        except ValueError as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")

    def run(self) -> None:
        """Запуск основного цикла текстового пользовательского интерфейса."""
        print("\n=== Добро пожаловать в базу студентов ===")

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
    """
    Функция для запуска TUI (совместимость с __main__.py).
    Создает экземпляр StudentTUI и запускает его.
    """
    app = StudentTUI()
    app.run()


if __name__ == "__main__":
    run()