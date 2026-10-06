import json
import os
from typing import Dict, List, Any
from storage.base import StorageBackend
from models.exceptions import DatabaseError


class JSONStorage(StorageBackend):
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def _get_table_file(self, table_name: str) -> str:
        return os.path.join(self.data_dir, f"{table_name}.json")

    def _get_id_file(self, table_name: str) -> str:
        return os.path.join(self.data_dir, f"{table_name}_id.json")

    def _get_schema_file(self, table_name: str) -> str:
        return os.path.join(self.data_dir, f"{table_name}_schema.json")

    def load_table(self, table_name: str, schema: Dict[str, type]) -> List[Dict]:
        table_file = self._get_table_file(table_name)
        if not os.path.exists(table_file):
            return []
        try:
            with open(table_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('records', [])
        except json.JSONDecodeError as e:
            raise DatabaseError(f"Invalid JSON in {table_file}: {e}")
        except IOError as e:
            raise DatabaseError(f"Cannot read {table_file}: {e}")

    def save_table(self, table_name: str, records: List[Dict]) -> None:
        table_file = self._get_table_file(table_name)
        try:
            with open(table_file, 'w', encoding='utf-8') as f:
                json.dump({'records': records}, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise DatabaseError(f"Cannot write {table_file}: {e}")

    def get_next_id(self, table_name: str) -> int:
        id_file = self._get_id_file(table_name)
        if os.path.exists(id_file):
            try:
                with open(id_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('next_id', 1)
            except (json.JSONDecodeError, IOError):
                return 1
        return 1

    def save_next_id(self, table_name: str, next_id: int) -> None:
        id_file = self._get_id_file(table_name)
        try:
            with open(id_file, 'w', encoding='utf-8') as f:
                json.dump({'next_id': next_id}, f)
        except IOError as e:
            raise DatabaseError(f"Cannot write {id_file}: {e}")

    def load_schema(self, table_name: str) -> Dict[str, type]:
        schema_file = self._get_schema_file(table_name)
        if os.path.exists(schema_file):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    type_map = {'str': str, 'int': int, 'float': float}
                    return {k: type_map.get(v, str) for k, v in data.items()}
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_schema(self, table_name: str, schema: Dict[str, type]) -> None:
        schema_file = self._get_schema_file(table_name)
        schema_str = {k: v.__name__ for k, v in schema.items()}
        try:
            with open(schema_file, 'w', encoding='utf-8') as f:
                json.dump(schema_str, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise DatabaseError(f"Cannot write {schema_file}: {e}")

    def delete_table(self, table_name: str) -> None:
        table_file = self._get_table_file(table_name)
        id_file = self._get_id_file(table_name)
        schema_file = self._get_schema_file(table_name)
        if os.path.exists(table_file):
            os.remove(table_file)
        if os.path.exists(id_file):
            os.remove(id_file)
        if os.path.exists(schema_file):
            os.remove(schema_file)

    def list_tables(self) -> List[str]:
        tables = []
        if not os.path.exists(self.data_dir):
            return tables
        for file in os.listdir(self.data_dir):
            if file.endswith('.json') and not file.endswith('_id.json') and not file.endswith('_schema.json'):
                tables.append(file.replace('.json', ''))
        return tables