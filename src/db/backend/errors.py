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