import json
import os
from typing import Dict, List, Any
from storage.json_storage import JSONStorage


class IndexedStorage(JSONStorage):
    def __init__(self, data_dir: str = "indexed_data"):
        super().__init__(data_dir)
        self.indexes: Dict[str, Dict[str, Dict[str, List[int]]]] = {}

    def _get_index_file(self, table_name: str, field: str) -> str:
        return os.path.join(self.data_dir, f"{table_name}_idx_{field}.json")

    def _load_index(self, table_name: str, field: str) -> Dict[str, List[int]]:
        index_file = self._get_index_file(table_name, field)
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_index(self, table_name: str, field: str, index: Dict[str, List[int]]) -> None:
        index_file = self._get_index_file(table_name, field)
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)

    def create_index(self, table_name: str, field: str) -> None:
        records = self.load_table(table_name, {})
        index = {}
        for record in records:
            value = str(record.get(field, ''))
            if value not in index:
                index[value] = []
            index[value].append(record['id'])
        if table_name not in self.indexes:
            self.indexes[table_name] = {}
        self.indexes[table_name][field] = index
        self._save_index(table_name, field, index)

    def get_by_index(self, table_name: str, field: str, value: Any) -> List[int]:
        if table_name in self.indexes and field in self.indexes[table_name]:
            str_value = str(value)
            return self.indexes[table_name][field].get(str_value, [])
        return []

    def save_table(self, table_name: str, records: List[Dict]) -> None:
        super().save_table(table_name, records)
        if table_name in self.indexes:
            for field in list(self.indexes[table_name].keys()):
                self.create_index(table_name, field)

    def delete_table(self, table_name: str) -> None:
        super().delete_table(table_name)
        if table_name in self.indexes:
            for field in list(self.indexes[table_name].keys()):
                index_file = self._get_index_file(table_name, field)
                if os.path.exists(index_file):
                    os.remove(index_file)
            del self.indexes[table_name]