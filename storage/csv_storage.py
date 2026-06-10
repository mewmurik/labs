import csv
import os
import json
from typing import Dict, List, Any
from storage.base import StorageBackend


class CSVStorage(StorageBackend):
    def __init__(self, data_dir: str = "csv_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def _get_table_file(self, table_name: str) -> str:
        return os.path.join(self.data_dir, f"{table_name}.csv")

    def _get_id_file(self, table_name: str) -> str:
        return os.path.join(self.data_dir, f"{table_name}_id.json")

    def _get_schema_file(self, table_name: str) -> str:
        return os.path.join(self.data_dir, f"{table_name}_schema.json")

    def load_table(self, table_name: str, schema: Dict[str, type]) -> List[Dict]:
        table_file = self._get_table_file(table_name)
        if not os.path.exists(table_file):
            return []
        records = []
        with open(table_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                record = {'id': int(row['id'])}
                for field, field_type in schema.items():
                    if field in row and row[field]:
                        if field_type == int:
                            record[field] = int(row[field])
                        elif field_type == float:
                            record[field] = float(row[field])
                        else:
                            record[field] = row[field]
                records.append(record)
        return records

    def save_table(self, table_name: str, records: List[Dict]) -> None:
        if not records:
            return
        table_file = self._get_table_file(table_name)
        fieldnames = ['id'] + [k for k in records[0].keys() if k != 'id']
        with open(table_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(record)

    def get_next_id(self, table_name: str) -> int:
        id_file = self._get_id_file(table_name)
        if os.path.exists(id_file):
            with open(id_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('next_id', 1)
        return 1

    def save_next_id(self, table_name: str, next_id: int) -> None:
        id_file = self._get_id_file(table_name)
        with open(id_file, 'w', encoding='utf-8') as f:
            json.dump({'next_id': next_id}, f)

    def load_schema(self, table_name: str) -> Dict[str, type]:
        schema_file = self._get_schema_file(table_name)
        if os.path.exists(schema_file):
            with open(schema_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                type_map = {'str': str, 'int': int, 'float': float}
                return {k: type_map.get(v, str) for k, v in data.items()}
        return {}

    def save_schema(self, table_name: str, schema: Dict[str, type]) -> None:
        schema_file = self._get_schema_file(table_name)
        schema_str = {k: v.__name__ for k, v in schema.items()}
        with open(schema_file, 'w', encoding='utf-8') as f:
            json.dump(schema_str, f, indent=2, ensure_ascii=False)

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
            if file.endswith('.csv'):
                tables.append(file.replace('.csv', ''))
        return tables