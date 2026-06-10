from abc import ABC, abstractmethod
from typing import Dict, List, Any


class StorageBackend(ABC):
    @abstractmethod
    def load_table(self, table_name: str, schema: Dict[str, type]) -> List[Dict]:
        pass

    @abstractmethod
    def save_table(self, table_name: str, records: List[Dict]) -> None:
        pass

    @abstractmethod
    def get_next_id(self, table_name: str) -> int:
        pass

    @abstractmethod
    def save_next_id(self, table_name: str, next_id: int) -> None:
        pass

    @abstractmethod
    def delete_table(self, table_name: str) -> None:
        pass

    @abstractmethod
    def list_tables(self) -> List[str]:
        pass

    @abstractmethod
    def load_schema(self, table_name: str) -> Dict[str, type]:
        pass

    @abstractmethod
    def save_schema(self, table_name: str, schema: Dict[str, type]) -> None:
        pass