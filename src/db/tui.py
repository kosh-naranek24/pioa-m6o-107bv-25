# Импортируем из модуля backend.memory функции, реализующие операции
# создания записи, выборки, обновления и удаления записей из таблицы.
from .backend.memory import create_record, select_record, update_record, delete_record


# Функция вывода текстового меню в консоль.
def _print_menu() -> None:
    # Символ \n обозначает перевод строки.
    print("\n=== База студентов ===")
    print("1. Добавить запись")
    print("2. Показать все записи")
    print("3. Найти записи по фильтру")
    print("4. Обновить запись")
    print("5. Удалить запись")
    print("0. Выход")


# Функция чтения целочисленного значения из консоли.
def _read_int(prompt: str) -> int:
    # Используется цикл с повторением до получения корректного ввода.
    while True:
        # Получение строки из консоли с удалением пробельных символов
        # в начале и в конце строки.
        raw = input(prompt).strip()
        try:
            # Преобразование строки к целому числу.
            return int(raw)
        except ValueError:
            # Исключение возникает при невозможности преобразования.
            # Пользователю выводится сообщение об ошибке,
            # после чего ввод повторяется.
            print("Ошибка: введите целое число.")


# Функция добавления новой записи в базу данных.
def _add_student() -> None:
    print("\nДобавление записи")

    student_id = _read_int("id: ")
    first_name = input("first_name: ").strip()
    second_name = input("second_name: ").strip()
    age = _read_int("age: ")
    sex = input("sex: ").strip()

    try:
        # Вызов функции слоя бизнес-логики.
        record = create_record(student_id, first_name, second_name, age, sex)

        # В случае успешного добавления запись выводится в консоль.
        print(f"Запись добавлена: {record}")

    except ValueError as exc:
        # Обработка ошибок валидации.
        print(f"Ошибка: {exc}")


# Вспомогательная функция вывода списка записей.
def _print_records(records: list[tuple[int, str, str, int, str]]) -> None:
    # Проверка на пустой список.
    if not records:
        print("Записи не найдены.")
        return

    # Последовательный вывод записей.
    for record in records:
        print(record)


# Функция вывода всех записей из базы данных.
def _show_all_students() -> None:
    print("\nСписок записей")
    _print_records(select_record())


# Функция чтения необязательного целочисленного значения.
# Пустой ввод интерпретируется как отсутствие фильтра (None).
def _read_optional_int(prompt: str) -> int | None:
    while True:
        raw = input(prompt).strip()

        if raw == "":
            return None

        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число или оставьте поле пустым.")


# Функция поиска записей по заданным фильтрам.
def _find_students_by_filter() -> None:
    print("\nПоиск по фильтру (Enter = пропустить поле)")

    student_id = _read_optional_int("id: ")

    # Оператор `or` возвращает первое истинное значение.
    # Если строка после strip() пуста, будет возвращено None.
    first_name = input("first_name: ").strip() or None
    second_name = input("second_name: ").strip() or None

    age = _read_optional_int("age: ")
    sex = input("sex: ").strip() or None

    records = select_record(
        student_id=student_id,
        first_name=first_name,
        second_name=second_name,
        age=age,
        sex=sex,
    )

    _print_records(records)


# Функция обновления существующей записи.
def _update_student() -> None:
    print("\nОбновление записи")

    # Получаем ID записи для обновления
    student_id = _read_int("Введите id записи для обновления: ")

    # Сначала проверяем, существует ли запись
    existing = select_record(student_id=student_id)
    if not existing:
        print(f"Запись с id={student_id} не найдена.")
        return

    print("Введите новые данные (Enter = оставить без изменений):")

    # Читаем новые значения (пустой ввод = None = оставить без изменений)
    first_name = input(f"first_name ({existing[0][1]}): ").strip() or None
    second_name = input(f"second_name ({existing[0][2]}): ").strip() or None
    age = _read_optional_int(f"age ({existing[0][3]}): ")
    sex = input(f"sex ({existing[0][4]}): ").strip() or None

    try:
        # Вызываем функцию обновления
        updated = update_record(
            student_id=student_id,
            first_name=first_name,
            second_name=second_name,
            age=age,
            sex=sex
        )

        if updated:
            print(f"Запись успешно обновлена: {updated}")
        else:
            print("Ошибка при обновлении записи.")

    except ValueError as exc:
        print(f"Ошибка: {exc}")


# Функция удаления записей.
def _delete_students() -> None:
    print("\nУдаление записей")
    print("Выберите способ удаления:")
    print("1. Удалить по id")
    print("2. Удалить по фильтру")

    choice = input("Ваш выбор: ").strip()

    if choice == "1":
        # Удаление по конкретному id
        student_id = _read_int("Введите id записи для удаления: ")

        deleted = delete_record(student_id=student_id)

    elif choice == "2":
        # Удаление по фильтру
        print("\nВведите фильтры для удаления (Enter = пропустить поле):")

        first_name = input("first_name: ").strip() or None
        second_name = input("second_name: ").strip() or None
        age = _read_optional_int("age: ")
        sex = input("sex: ").strip() or None

        # Сначала показываем, какие записи будут удалены
        to_delete = select_record(
            first_name=first_name,
            second_name=second_name,
            age=age,
            sex=sex
        )

        if not to_delete:
            print("Записи, соответствующие фильтру, не найдены.")
            return

        print("\nБудут удалены следующие записи:")
        _print_records(to_delete)

        deleted = delete_record(
            first_name=first_name,
            second_name=second_name,
            age=age,
            sex=sex
        )
        print(f"Удалено записей: {len(deleted)}")

    else:
        print("Неверный выбор.")


def run() -> None:
    """
    Запускает основной цикл текстового пользовательского интерфейса.

    Цикл выполняется до тех пор, пока пользователь явно
    не выберет завершение программы.
    """
    while True:
        # Отображение меню доступных действий.
        _print_menu()

        # Получение команды пользователя.
        # Метод strip() удаляет пробельные символы
        # в начале и в конце строки.
        action = input("Выберите действие: ").strip()

        # Диспетчеризация пользовательской команды.
        if action == "1":
            _add_student()

        elif action == "2":
            _show_all_students()

        elif action == "3":
            _find_students_by_filter()

        elif action == "4":
            _update_student()

        elif action == "5":
            _delete_students()

        elif action == "0":
            # Завершение работы программы.
            print("Выход из программы.")
            break

        else:
            # Обработка некорректного ввода команды.
            print("Неизвестная команда. Повторите ввод.")