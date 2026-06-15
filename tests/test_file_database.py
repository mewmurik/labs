import pytest
import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.file_database import FileDatabase
from storage.json_storage import JSONStorage
from storage.csv_storage import CSVStorage
from models.exceptions import RecordNotFoundError, InvalidInputError, DatabaseError


class TestJSONFileDatabase:
    def setup_method(self):
        self.test_dir = "test_json_data"
        storage = JSONStorage(self.test_dir)
        self.db = FileDatabase(storage)

    def teardown_method(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_table(self):
        self.db.create_table('Users', {'name': str, 'age': int})
        assert 'Users' in self.db.tables

    def test_add_and_persist(self):
        table = self.db.create_table('Users', {'name': str, 'age': int})
        table.add(name='Alice', age=30)
        assert len(table.records) == 1

        new_db = FileDatabase(JSONStorage(self.test_dir))
        new_table = new_db.get_table('Users')
        assert len(new_table.records) == 1
        assert new_table.get(1)['name'] == 'Alice'

    def test_update_and_persist(self):
        table = self.db.create_table('Users', {'name': str, 'age': int})
        table.add(name='Alice', age=30)
        table.update(1, age=31)

        new_db = FileDatabase(JSONStorage(self.test_dir))
        new_table = new_db.get_table('Users')
        assert new_table.get(1)['age'] == 31

    def test_delete_and_persist(self):
        table = self.db.create_table('Users', {'name': str, 'age': int})
        table.add(name='Alice', age=30)
        table.delete(1)

        new_db = FileDatabase(JSONStorage(self.test_dir))
        new_table = new_db.get_table('Users')
        assert len(new_table.records) == 0

    def test_drop_table(self):
        self.db.create_table('Users', {'name': str, 'age': int})
        self.db.drop_table('Users')
        assert 'Users' not in self.db.tables

        new_db = FileDatabase(JSONStorage(self.test_dir))
        assert 'Users' not in new_db.tables


class TestCSVFileDatabase:
    def setup_method(self):
        self.test_dir = "test_csv_data"
        storage = CSVStorage(self.test_dir)
        self.db = FileDatabase(storage)

    def teardown_method(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_table(self):
        self.db.create_table('Users', {'name': str, 'age': int})
        assert 'Users' in self.db.tables

    def test_add_and_persist(self):
        table = self.db.create_table('Users', {'name': str, 'age': int})
        table.add(name='Alice', age=30)

        new_db = FileDatabase(CSVStorage(self.test_dir))
        new_table = new_db.get_table('Users')
        assert len(new_table.records) == 1
        assert new_table.get(1)['name'] == 'Alice'