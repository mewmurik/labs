from typing import Dict, List, Any, Optional
from .exceptions import RecordNotFoundError, InvalidInputError, DatabaseError


class Table:
    def __init__(self, name: str, schema: Dict[str, type]):
        self.name = name
        self.schema = schema
        self.records: List[Dict[str, Any]] = []
        self._next_id = 1

    def add(self, **kwargs) -> int:
        for field, field_type in self.schema.items():
            if field not in kwargs:
                raise InvalidInputError(f"Field '{field}' is required")
            if not isinstance(kwargs[field], field_type):
                raise InvalidInputError(f"Field '{field}' must be {field_type.__name__}")

        record = {'id': self._next_id}
        record.update(kwargs)
        self.records.append(record)
        self._next_id += 1
        return record['id']

    def get(self, record_id: Optional[int] = None, filters: Optional[Dict] = None) -> Any:
        result = self.records.copy()

        if record_id is not None:
            for record in result:
                if record['id'] == record_id:
                    return record
            raise RecordNotFoundError(f"Record with id={record_id} not found")

        if filters:
            for key, value in filters.items():
                result = [r for r in result if r.get(key) == value]

        return result

    def get_all(self) -> List[Dict]:
        return self.records.copy()

    def update(self, record_id: int, **kwargs) -> Dict:
        record = self.get(record_id)
        for key, value in kwargs.items():
            if key in self.schema:
                if not isinstance(value, self.schema[key]):
                    raise InvalidInputError(f"Field '{key}' must be {self.schema[key].__name__}")
                record[key] = value
        return record

    def delete(self, record_id: int) -> bool:
        record = self.get(record_id)
        self.records.remove(record)
        return True

    def sort(self, key: str, reverse: bool = False) -> List[Dict]:
        if key not in self.schema and key != 'id':
            raise InvalidInputError(f"Field '{key}' does not exist")

        def get_value(record):
            return record.get(key)

        return sorted(self.records, key=get_value, reverse=reverse)


class Database:
    def __init__(self):
        self.tables: Dict[str, Table] = {}

    def create_table(self, name: str, schema: Dict[str, type]) -> Table:
        if name in self.tables:
            raise DatabaseError(f"Table '{name}' already exists")
        self.tables[name] = Table(name, schema)
        return self.tables[name]

    def get_table(self, name: str) -> Table:
        if name not in self.tables:
            raise DatabaseError(f"Table '{name}' does not exist")
        return self.tables[name]

    def drop_table(self, name: str) -> bool:
        if name not in self.tables:
            raise DatabaseError(f"Table '{name}' does not exist")
        del self.tables[name]
        return True

    def list_tables(self) -> List[str]:
        return list(self.tables.keys())