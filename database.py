from exceptions import RecordNotFoundError, InvalidInputError

class Table:
    def __init__(self, name, schema):
        self.name = name
        self.schema = schema  # {'field_name': type}
        self.records = []
        self._next_id = 1

    def add(self, **kwargs):
        """Добавление записи"""
        # Проверка полей
        for field, field_type in self.schema.items():
            if field not in kwargs:
                raise InvalidInputError(f"Поле '{field}' обязательно")
            if not isinstance(kwargs[field], field_type):
                raise InvalidInputError(f"Поле '{field}' должно быть типа {field_type.__name__}")

        record = {'id': self._next_id}
        record.update(kwargs)
        self.records.append(record)
        self._next_id += 1
        return record['id']

    def get(self, record_id=None, filters=None):
        """Чтение записей с фильтрацией"""
        result = self.records.copy()

        if record_id is not None:
            for record in result:
                if record['id'] == record_id:
                    return record
            raise RecordNotFoundError(f"Запись с id={record_id} не найдена")

        if filters:
            for key, value in filters.items():
                result = [r for r in result if r.get(key) == value]

        return result

    def update(self, record_id, **kwargs):
        """Обновление записи"""
        record = self.get(record_id)
        for key, value in kwargs.items():
            if key in self.schema:
                if not isinstance(value, self.schema[key]):
                    raise InvalidInputError(f"Поле '{key}' должно быть типа {self.schema[key].__name__}")
                record[key] = value
        return record

    def delete(self, record_id):
        """Удаление записи"""
        record = self.get(record_id)
        self.records.remove(record)
        return True


class Database:
    def __init__(self):
        self.tables = {}

    def create_table(self, name, schema):
        """Создание новой таблицы"""
        if name in self.tables:
            raise DatabaseError(f"Таблица '{name}' уже существует")
        self.tables[name] = Table(name, schema)
        return self.tables[name]

    def get_table(self, name):
        """Получение таблицы по имени"""
        if name not in self.tables:
            raise DatabaseError(f"Таблица '{name}' не существует")
        return self.tables[name]