class RecordNotFoundError(Exception):
    """Запись не найдена"""
    pass

class InvalidInputError(Exception):
    """Некорректный ввод"""
    pass

class DatabaseError(Exception):
    """Общая ошибка базы данных"""
    pass