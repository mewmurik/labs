import os
from typing import Dict, List, Any, Optional
from models.database import Table
from models.exceptions import DatabaseError, RecordNotFoundError, InvalidInputError
from storage.base import StorageBackend
from storage.json_storage import JSONStorage


class FileTable(Table):
    def __init__(self, name: str, schema: Dict[str, type], storage: StorageBackend):
        self.storage = storage
        self.name = name
        self.schema = schema
        self.records: List[Dict[str, Any]] = []
        self._next_id = 1
        self._load_from_storage()

    def _load_from_storage(self) -> None:
        self.records = self.storage.load_table(self.name, self.schema)
        self._next_id = self.storage.get_next_id(self.name)
        if self.records:
            max_id = max(r['id'] for r in self.records)
            self._next_id = max(max_id + 1, self._next_id)
        if self._next_id < 1:
            self._next_id = 1

    def _save_to_storage(self) -> None:
        self.storage.save_table(self.name, self.records)
        self.storage.save_next_id(self.name, self._next_id)
        self.storage.save_schema(self.name, self.schema)

    def add(self, **kwargs) -> int:
        record_id = super().add(**kwargs)
        self._save_to_storage()
        return record_id

    def update(self, record_id: int, **kwargs) -> Dict:
        result = super().update(record_id, **kwargs)
        self._save_to_storage()
        return result

    def delete(self, record_id: int) -> bool:
        result = super().delete(record_id)
        self._save_to_storage()
        return result

    def get_all(self) -> List[Dict]:
        return self.records.copy()

    def get(self, record_id: Optional[int] = None, filters: Optional[Dict] = None) -> Any:
        result = self.records.copy()

        if record_id is not None:
            for record in result:
                if record['id'] == record_id:
                    return record
            raise RecordNotFoundError(f"Record with id={record_id} not found")

        if filters:
            if hasattr(self.storage, 'get_by_index'):
                for field, value in filters.items():
                    ids = self.storage.get_by_index(self.name, field, value)
                    if ids:
                        result = [r for r in result if r['id'] in ids]
                        return result

            for key, value in filters.items():
                result = [r for r in result if r.get(key) == value]

        return result

    def sort(self, key: str, reverse: bool = False) -> List[Dict]:
        if key not in self.schema and key != 'id':
            raise InvalidInputError(f"Field '{key}' does not exist")

        def get_value(record):
            return record.get(key)

        return sorted(self.records, key=get_value, reverse=reverse)


class FileDatabase:
    def __init__(self, storage: Optional[StorageBackend] = None):
        self.storage = storage or JSONStorage()
        self.tables: Dict[str, FileTable] = {}
        self._load_all_tables()

    def _load_all_tables(self) -> None:
        for table_name in self.storage.list_tables():
            self._load_table(table_name)

    def _load_table(self, table_name: str) -> Optional[FileTable]:
        schema = self.storage.load_schema(table_name)
        if not schema:
            records = self.storage.load_table(table_name, {})
            if not records:
                return None
            schema = {}
            for record in records:
                for key, value in record.items():
                    if key != 'id' and key not in schema:
                        if isinstance(value, int):
                            schema[key] = int
                        elif isinstance(value, float):
                            schema[key] = float
                        else:
                            schema[key] = str
        if schema:
            table = FileTable(table_name, schema, self.storage)
            self.tables[table_name] = table
            return table
        return None

    def create_table(self, name: str, schema: Dict[str, type]) -> FileTable:
        if name in self.tables:
            raise DatabaseError(f"Table '{name}' already exists")
        table = FileTable(name, schema, self.storage)
        self.tables[name] = table
        table._save_to_storage()
        return table

    def get_table(self, name: str) -> FileTable:
        if name not in self.tables:
            self._load_table(name)
            if name not in self.tables:
                raise DatabaseError(f"Table '{name}' does not exist")
        return self.tables[name]

    def drop_table(self, name: str) -> bool:
        if name not in self.tables:
            raise DatabaseError(f"Table '{name}' does not exist")
        self.storage.delete_table(name)
        del self.tables[name]
        return True

    def list_tables(self) -> List[str]:
        storage_tables = self.storage.list_tables()
        for table_name in storage_tables:
            if table_name not in self.tables:
                self._load_table(table_name)
        return list(self.tables.keys())