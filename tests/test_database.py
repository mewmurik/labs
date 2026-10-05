import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Database, Table
from models.exceptions import RecordNotFoundError, InvalidInputError, DatabaseError


class TestTable:
    def setup_method(self):
        self.schema = {'name': str, 'age': int}
        self.table = Table('Users', self.schema)

    def test_add_record(self):
        record_id = self.table.add(name='Alice', age=30)
        assert record_id == 1
        assert len(self.table.records) == 1

    def test_add_record_missing_field(self):
        with pytest.raises(InvalidInputError):
            self.table.add(name='Alice')

    def test_add_record_wrong_type(self):
        with pytest.raises(InvalidInputError):
            self.table.add(name='Alice', age='thirty')

    def test_get_all_records(self):
        self.table.add(name='Alice', age=30)
        self.table.add(name='Bob', age=25)
        records = self.table.get_all()
        assert len(records) == 2

    def test_get_by_id(self):
        self.table.add(name='Alice', age=30)
        record = self.table.get(1)
        assert record['name'] == 'Alice'

    def test_get_by_id_not_found(self):
        with pytest.raises(RecordNotFoundError):
            self.table.get(999)

    def test_get_with_filters(self):
        self.table.add(name='Alice', age=30)
        self.table.add(name='Bob', age=25)
        self.table.add(name='Alice', age=35)
        results = self.table.get(filters={'name': 'Alice'})
        assert len(results) == 2

    def test_update_record(self):
        self.table.add(name='Alice', age=30)
        self.table.update(1, age=31)
        record = self.table.get(1)
        assert record['age'] == 31

    def test_update_nonexistent_record(self):
        with pytest.raises(RecordNotFoundError):
            self.table.update(999, age=30)

    def test_delete_record(self):
        self.table.add(name='Alice', age=30)
        assert len(self.table.records) == 1
        self.table.delete(1)
        assert len(self.table.records) == 0

    def test_delete_nonexistent_record(self):
        with pytest.raises(RecordNotFoundError):
            self.table.delete(999)

    def test_sort_ascending(self):
        self.table.add(name='Bob', age=30)
        self.table.add(name='Alice', age=25)
        self.table.add(name='Charlie', age=35)
        sorted_records = self.table.sort('age', reverse=False)
        assert sorted_records[0]['age'] == 25
        assert sorted_records[1]['age'] == 30
        assert sorted_records[2]['age'] == 35

    def test_sort_descending(self):
        self.table.add(name='Bob', age=30)
        self.table.add(name='Alice', age=25)
        self.table.add(name='Charlie', age=35)
        sorted_records = self.table.sort('age', reverse=True)
        assert sorted_records[0]['age'] == 35
        assert sorted_records[1]['age'] == 30
        assert sorted_records[2]['age'] == 25

    def test_sort_invalid_field(self):
        with pytest.raises(InvalidInputError):
            self.table.sort('invalid_field')


class TestDatabase:
    def setup_method(self):
        self.db = Database()

    def test_create_table(self):
        table = self.db.create_table('Users', {'name': str})
        assert 'Users' in self.db.tables

    def test_create_duplicate_table(self):
        self.db.create_table('Users', {'name': str})
        with pytest.raises(DatabaseError):
            self.db.create_table('Users', {'name': str})

    def test_get_table(self):
        self.db.create_table('Users', {'name': str})
        table = self.db.get_table('Users')
        assert table.name == 'Users'

    def test_get_nonexistent_table(self):
        with pytest.raises(DatabaseError):
            self.db.get_table('Nonexistent')

    def test_drop_table(self):
        self.db.create_table('Users', {'name': str})
        assert 'Users' in self.db.tables
        self.db.drop_table('Users')
        assert 'Users' not in self.db.tables

    def test_list_tables(self):
        self.db.create_table('Users', {'name': str})
        self.db.create_table('Products', {'price': float})
        tables = self.db.list_tables()
        assert 'Users' in tables
        assert 'Products' in tables
        assert len(tables) == 2