from .errors import DuplicateIDError, InvalidAgeError, StudentNotFoundError

type StudentRecord = tuple[int, str, str, int, str]


class StudentTable:


    def __init__(self) -> None:
        """Инициализация пустой таблицы."""
        self._students: list[StudentRecord] = []

    def create_record(
            self,
            student_id: int,
            first_name: str,
            second_name: str,
            age: int,
            sex: str,
    ) -> StudentRecord:

        if age < 0:
            raise InvalidAgeError(f"Некорректный возраст: {age}")

        if self._find_index_by_id(student_id) is not None:
            raise DuplicateIDError(f"Запись с id={student_id} уже существует.")

        new_record: StudentRecord = (
            student_id,
            first_name.strip(),
            second_name.strip(),
            age,
            sex.strip(),
        )
        self._students.append(new_record)
        return new_record

    def select_record(
            self,
            student_id: int | None = None,
            first_name: str | None = None,
            second_name: str | None = None,
            age: int | None = None,
            sex: str | None = None,
    ) -> list[StudentRecord]:

        # Если все фильтры None - возвращаем копию
        if all(p is None for p in [student_id, first_name, second_name, age, sex]):
            return self._students.copy()

        result: list[StudentRecord] = []
        for record in self._students:
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
            result.append(record)
        return result

    def update_record(
            self,
            student_id: int,
            first_name: str | None = None,
            second_name: str | None = None,
            age: int | None = None,
            sex: str | None = None,
    ) -> StudentRecord:

        index = self._find_index_by_id(student_id)
        if index is None:
            raise StudentNotFoundError(f"Запись с id={student_id} не найдена.")

        current = self._students[index]

        if age is not None and age < 0:
            raise InvalidAgeError(f"Некорректный возраст: {age}")

        updated: StudentRecord = (
            current[0],  # ID не меняется
            first_name.strip() if first_name is not None else current[1],
            second_name.strip() if second_name is not None else current[2],
            age if age is not None else current[3],
            sex.strip() if sex is not None else current[4],
        )

        self._students[index] = updated
        return updated

    def delete_record(
            self,
            student_id: int | None = None,
            first_name: str | None = None,
            second_name: str | None = None,
            age: int | None = None,
            sex: str | None = None,
    ) -> list[StudentRecord]:

        deleted: list[StudentRecord] = []

        # Если указан ID - удаляем конкретную запись
        if student_id is not None:
            index = self._find_index_by_id(student_id)
            if index is not None:
                deleted.append(self._students.pop(index))
            return deleted

        # Иначе удаляем по фильтрам
        indices_to_delete: list[int] = []
        for i, record in enumerate(self._students):
            matches = True
            if first_name is not None and record[1] != first_name:
                matches = False
            if second_name is not None and record[2] != second_name:
                matches = False
            if age is not None and record[3] != age:
                matches = False
            if sex is not None and record[4] != sex:
                matches = False

            if matches:
                indices_to_delete.append(i)

        # Удаляем с конца, чтобы не сбивать индексы
        for index in reversed(indices_to_delete):
            deleted.append(self._students.pop(index))

        return deleted

    def _find_index_by_id(self, student_id: int) -> int | None:

        for i, record in enumerate(self._students):
            if record[0] == student_id:
                return i
        return None

    def count(self) -> int:
        """Возвращает количество записей."""
        return len(self._students)

    def clear(self) -> None:
        """Очищает таблицу."""
        self._students.clear()