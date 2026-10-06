import pytest
import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.json_storage import JSONStorage
from storage.csv_storage import CSVStorage
from storage.indexed_storage import IndexedStorage
from models.exceptions import DatabaseError


class TestJSONStorage:
    def setup_method(self):
        self.test_dir = "test_json_storage"
        self.storage = JSONStorage(self.test_dir)

    def teardown_method(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_and_load(self):
        records = [{'id': 1, 'name': 'Alice', 'age': 30}]
        self.storage.save_table('Users', records)
        loaded = self.storage.load_table('Users', {'name': str, 'age': int})
        assert len(loaded) == 1
        assert loaded[0]['name'] == 'Alice'

    def test_load_nonexistent(self):
        assert self.storage.load_table('Nonexistent', {}) == []

    def test_next_id(self):
        assert self.storage.get_next_id('Users') == 1
        self.storage.save_next_id('Users', 5)
        assert self.storage.get_next_id('Users') == 5

    def test_schema(self):
        schema = {'name': str, 'age': int}
        self.storage.save_schema('Users', schema)
        loaded = self.storage.load_schema('Users')
        assert loaded['name'] is str
        assert loaded['age'] is int

    def test_load_schema_nonexistent(self):
        assert self.storage.load_schema('Nonexistent') == {}

    def test_list_tables(self):
        self.storage.save_table('Users', [{'id': 1, 'name': 'A'}])
        self.storage.save_table('Products', [{'id': 1, 'title': 'X'}])
        tables = self.storage.list_tables()
        assert 'Users' in tables
        assert 'Products' in tables

    def test_delete_table(self):
        self.storage.save_table('Users', [{'id': 1}])
        self.storage.save_schema('Users', {'name': str})
        self.storage.delete_table('Users')
        assert 'Users' not in self.storage.list_tables()


class TestCSVStorage:
    def setup_method(self):
        self.test_dir = "test_csv_storage"
        self.storage = CSVStorage(self.test_dir)

    def teardown_method(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_and_load(self):
        records = [{'id': 1, 'name': 'Alice', 'age': 30}]
        self.storage.save_table('Users', records)
        loaded = self.storage.load_table('Users', {'name': str, 'age': int})
        assert len(loaded) == 1
        assert loaded[0]['name'] == 'Alice'

    def test_save_empty_table(self):
        self.storage.save_table('Empty', [])
        assert os.path.exists(os.path.join(self.test_dir, 'Empty.csv'))

    def test_load_nonexistent(self):
        assert self.storage.load_table('Nonexistent', {}) == []

    def test_next_id(self):
        assert self.storage.get_next_id('Users') == 1
        self.storage.save_next_id('Users', 3)
        assert self.storage.get_next_id('Users') == 3

    def test_schema(self):
        schema = {'name': str, 'age': int}
        self.storage.save_schema('Users', schema)
        loaded = self.storage.load_schema('Users')
        assert loaded['name'] is str

    def test_load_schema_nonexistent(self):
        assert self.storage.load_schema('Nonexistent') == {}

    def test_list_tables(self):
        self.storage.save_table('Users', [{'id': 1, 'name': 'A'}])
        tables = self.storage.list_tables()
        assert 'Users' in tables

    def test_delete_table(self):
        self.storage.save_table('Users', [{'id': 1, 'name': 'A'}])
        self.storage.save_schema('Users', {'name': str})
        self.storage.delete_table('Users')
        assert 'Users' not in self.storage.list_tables()


class TestIndexedStorage:
    def setup_method(self):
        self.test_dir = "test_indexed_storage"
        self.storage = IndexedStorage(self.test_dir)

    def teardown_method(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_index(self):
        records = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
        self.storage.save_table('Users', records)
        self.storage.create_index('Users', 'name')
        ids = self.storage.get_by_index('Users', 'name', 'Alice')
        assert 1 in ids

    def test_get_by_index_not_found(self):
        records = [{'id': 1, 'name': 'Alice'}]
        self.storage.save_table('Users', records)
        self.storage.create_index('Users', 'name')
        assert self.storage.get_by_index('Users', 'name', 'X') == []

    def test_get_by_index_no_index(self):
        assert self.storage.get_by_index('Users', 'name', 'X') == []

    def test_drop_index(self):
        records = [{'id': 1, 'name': 'Alice'}]
        self.storage.save_table('Users', records)
        self.storage.create_index('Users', 'name')
        self.storage.drop_index('Users', 'name')
        assert self.storage.get_by_index('Users', 'name', 'Alice') == []

    def test_drop_nonexistent_index(self):
        self.storage.drop_index('Users', 'name')

    def test_index_rebuilt_on_save(self):
        records = [{'id': 1, 'name': 'Alice'}]
        self.storage.save_table('Users', records)
        self.storage.create_index('Users', 'name')
        records.append({'id': 2, 'name': 'Bob'})
        self.storage.save_table('Users', records)
        ids = self.storage.get_by_index('Users', 'name', 'Bob')
        assert 2 in ids

    def test_delete_table_with_index(self):
        records = [{'id': 1, 'name': 'Alice'}]
        self.storage.save_table('Users', records)
        self.storage.create_index('Users', 'name')
        self.storage.delete_table('Users')
        assert 'Users' not in self.storage.list_tables()