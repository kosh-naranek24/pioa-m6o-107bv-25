# Определение пользовательского алиаса типа для записи таблицы.
# В качестве структуры записи используется кортеж,
# поскольку кортеж является неизменяемым типом данных.
# Структура записи Student: (id, first_name, second_name, age, sex)
type StudentRecord = tuple[int, str, str, int, str]

# Таблица Student представлена списком записей (кортежей).
Student: list[StudentRecord] = []


def create_record(
    student_id: int,   # Уникальный идентификатор записи
    first_name: str,   # Имя
    second_name: str,  # Фамилия
    age: int,          # Возраст
    sex: str,          # Пол
) -> StudentRecord:
    """
    Создаёт новую запись и добавляет её в таблицу Student.

    Выполняется валидация возраста и проверка уникальности идентификатора.
    В случае нарушения условий возбуждается исключение ValueError.
    """

    # Проверка корректности возраста.
    # Возраст не может быть отрицательным значением.
    if age < 0:
        raise ValueError("Поле age не может быть отрицательным.")

    # Проверка уникальности идентификатора.
    # Функция any() возвращает True, если хотя бы один элемент
    # последовательности удовлетворяет условию.
    if any(record[0] == student_id for record in Student):
        raise ValueError(f"Запись с id={student_id} уже существует.")

    # Формирование новой записи.
    # Метод strip() удаляет пробельные символы
    # в начале и в конце строки.
    new_record: StudentRecord = (
        student_id,
        first_name.strip(),
        second_name.strip(),
        age,
        sex.strip(),
    )

    # Добавление записи в таблицу.
    Student.append(new_record)

    # Возврат созданной записи.
    return new_record


def select_record(
    student_id: int | None = None,   # Фильтр по идентификатору
    first_name: str | None = None,   # Фильтр по имени
    second_name: str | None = None,  # Фильтр по фамилии
    age: int | None = None,          # Фильтр по возрасту
    sex: str | None = None,          # Фильтр по полу
) -> list[StudentRecord]:
    """
    Выполняет выборку записей из таблицы Student
    в соответствии с переданными фильтрами.

    Если фильтры не заданы, возвращается копия всей таблицы.
    """

    # Проверка отсутствия всех фильтров.
    # В этом случае возвращается копия списка,
    # чтобы предотвратить изменение исходной таблицы
    # внешним кодом.
    if (
        student_id is None
        and first_name is None
        and second_name is None
        and age is None
        and sex is None
    ):
        return Student.copy()

    # Формирование результирующего списка.
    result: list[StudentRecord] = []

    # Итерация по всем записям таблицы.
    for record in Student:

        # Проверка соответствия каждому фильтру.
        # Если фильтр задан и запись ему не соответствует,
        # выполняется переход к следующей итерации цикла.

        if student_id is not None and record[0] != student_id:
            continue

        if first_name is not None and record[1] != first_name:
            continue

        if second_name is not None and record[2] != second_name:
            continue

        if age is not None and record[3] != age:
            continue

        if sex is not None and record[4] != sex:
            continue

        # Если запись удовлетворяет всем заданным условиям,
        # она добавляется в результирующий список.
        result.append(record)

    # Возврат списка найденных записей.
    return result


def update_record(
        student_id: int | None = None,  # Идентификатор обновляемой записи
        first_name: str | None = None,  # Новое имя (если указано)
        second_name: str | None = None,  # Новая фамилия (если указано)
        age: int | None = None,  # Новый возраст (если указан)
        sex: str | None = None,  # Новый пол (если указан)
) -> StudentRecord | None:
    """
    Обновляет поля существующей записи по идентификатору.

    Если запись с указанным student_id найдена, обновляет её поля.
    Возвращает обновлённую запись или None, если запись не найдена.
    """

    # Поиск индекса записи с указанным идентификатором
    index_to_update = None
    for i, record in enumerate(Student):
        if record[0] == student_id:
            index_to_update = i
            break

    # Если запись не найдена, возвращаем None
    if index_to_update is None:
        return None

    # Получаем текущую запись
    current_record = Student[index_to_update]

    # Формируем обновлённую запись (если поле не указано для обновления, оставляем старое значение)
    updated_record: StudentRecord = (
        current_record[0],  # id не может быть изменён
        first_name.strip() if first_name is not None else current_record[1],
        second_name.strip() if second_name is not None else current_record[2],
        age if age is not None else current_record[3],
        sex.strip() if sex is not None else current_record[4],
    )

    # Валидация обновлённых данных
    if updated_record[3] < 0:
        raise ValueError("Поле age не может быть отрицательным.")

    # Заменяем запись в таблице
    Student[index_to_update] = updated_record

    return updated_record


def delete_record(
        student_id: int | None = None,  # Идентификатор удаляемой записи
        first_name: str | None = None,  # Фильтр по имени
        second_name: str | None = None,  # Фильтр по фамилии
        age: int | None = None,  # Фильтр по возрасту
        sex: str | None = None,  # Фильтр по полу
) -> list[StudentRecord]:
    """
    Удаляет записи из таблицы по идентификатору или фильтру.

    Если указан student_id, удаляет только запись с этим ID.
    Если student_id не указан, удаляет все записи, соответствующие фильтрам.

    Возвращает список удалённых записей.
    """

    deleted_records: list[StudentRecord] = []

    # Если указан конкретный ID, удаляем только одну запись
    if student_id is not None:
        for i, record in enumerate(Student):
            if record[0] == student_id:
                deleted_records.append(Student.pop(i))
                return deleted_records
        return deleted_records  # Запись не найдена

    # Иначе удаляем по фильтрам (или все записи, если фильтров нет)
    indices_to_delete: list[int] = []

    for i, record in enumerate(Student):
        flag = True

        if first_name is not None and record[1] != first_name:
            flag = False
        if second_name is not None and record[2] != second_name:
            flag = False
        if age is not None and record[3] != age:
            flag = False
        if sex is not None and record[4] != sex:
            flag = False

        if flag:
            indices_to_delete.append(i)

    # Удаляем записи с конца списка, чтобы не нарушать индексацию
    for index in reversed(indices_to_delete):
        deleted_records.append(Student.pop(index))

    return deleted_records