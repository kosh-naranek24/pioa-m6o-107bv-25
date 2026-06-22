class StudentTableError(Exception):
    """Базовое исключение для ошибок таблицы студентов."""
    pass


class InvalidAgeError(StudentTableError):
    """Ошибка при некорректном возрасте."""
    pass


class DuplicateIDError(StudentTableError):
    """Ошибка при дублировании ID."""
    pass


class StudentNotFoundError(StudentTableError):
    """Ошибка при поиске несуществующего студента."""
    pass


class DatabaseError(Exception):
    """Базовый класс для ошибок базы данных."""


class TableAlreadyExistsError(DatabaseError):
    """Ошибка, возникающая при попытке создать уже существующую таблицу."""


class TableNotFoundError(DatabaseError):
    """Ошибка, возникающая при обращении к несуществующей таблице."""


class MissingColumnError(DatabaseError):
    """Ошибка, возникающая при отсутствии обязательного поля в записи."""


class UnknownColumnError(DatabaseError):
    """Ошибка, возникающая при использовании поля, которого нет в схеме таблицы."""


class InvalidStorageDataError(DatabaseError):
    """Ошибка, возникающая при чтении повреждённых данных из файла."""