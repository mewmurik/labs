import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Database
from ui.console import ConsoleInterface


class TestConsoleInterfaceInit:
    def test_init_with_db(self):
        db = Database()
        ui = ConsoleInterface(db)
        assert ui.db is db
        assert ui.current_table is None

    def test_init_without_db(self):
        ui = ConsoleInterface()
        assert ui.db is not None
        assert ui.current_table is None


class TestCreateTable:
    def setup_method(self):
        self.db = Database()
        self.ui = ConsoleInterface(self.db)

    def test_create_table_success(self):
        with patch('builtins.input', side_effect=['Users', 'name:str', 'age:int', 'done']):
            with patch('builtins.print'):
                self.ui._create_table()
        assert 'Users' in self.db.tables

    def test_create_table_empty_name(self):
        with patch('builtins.input', return_value=''):
            with patch('builtins.print'):
                self.ui._create_table()
        assert len(self.db.tables) == 0

    def test_create_table_invalid_format(self):
        with patch('builtins.input', side_effect=['Users', 'name', 'name:str', 'done']):
            with patch('builtins.print'):
                self.ui._create_table()
        assert 'Users' in self.db.tables

    def test_create_table_unknown_type(self):
        with patch('builtins.input', side_effect=['Users', 'name:unknown', 'name:str', 'done']):
            with patch('builtins.print'):
                self.ui._create_table()
        assert 'Users' in self.db.tables

    def test_create_table_no_fields(self):
        with patch('builtins.input', side_effect=['Users', 'done']):
            with patch('builtins.print'):
                self.ui._create_table()
        assert 'Users' not in self.db.tables

    def test_create_table_duplicate(self):
        self.db.create_table('Users', {'name': str})
        with patch('builtins.input', side_effect=['Users', 'name:str', 'done']):
            with patch('builtins.print') as mock_print:
                self.ui._create_table()
                assert mock_print.called


class TestListTables:
    def setup_method(self):
        self.db = Database()
        self.ui = ConsoleInterface(self.db)

    def test_list_tables_empty(self):
        with patch('builtins.print') as mock_print:
            self.ui._list_tables()
            mock_print.assert_any_call("No tables created")

    def test_list_tables_with_data(self):
        self.db.create_table('Users', {'name': str})
        self.db.create_table('Products', {'price': float})
        with patch('builtins.print') as mock_print:
            self.ui._list_tables()
            assert mock_print.called


class TestSelectTable:
    def setup_method(self):
        self.db = Database()
        self.ui = ConsoleInterface(self.db)

    def test_select_no_tables(self):
        with patch('builtins.print') as mock_print:
            self.ui._select_table()
            mock_print.assert_any_call("No tables created")

    def test_select_table_success(self):
        self.db.create_table('Users', {'name': str})
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print'):
                self.ui._select_table()
        assert self.ui.current_table is not None
        assert self.ui.current_table.name == 'Users'

    def test_select_table_invalid_number(self):
        self.db.create_table('Users', {'name': str})
        with patch('builtins.input', return_value='99'):
            with patch('builtins.print'):
                self.ui._select_table()
        assert self.ui.current_table is None

    def test_select_table_invalid_input(self):
        self.db.create_table('Users', {'name': str})
        with patch('builtins.input', return_value='abc'):
            with patch('builtins.print'):
                self.ui._select_table()
        assert self.ui.current_table is None


class TestAddRecord:
    def setup_method(self):
        self.db = Database()
        self.ui = ConsoleInterface(self.db)
        self.db.create_table('Users', {'name': str, 'age': int})
        self.ui.current_table = self.db.get_table('Users')

    def test_add_record(self):
        with patch('builtins.input', side_effect=['Alice', '30']):
            with patch('builtins.print'):
                self.ui._add_record()
        assert len(self.ui.current_table.records) == 1


class TestShowRecords:
    def setup_method(self):
        self.db = Database()
        self.ui = ConsoleInterface(self.db)
        self.db.create_table('Users', {'name': str})
        self.ui.current_table = self.db.get_table('Users')

    def test_show_empty(self):
        with patch('builtins.print') as mock_print:
            self.ui._show_all_records()
            mock_print.assert_any_call("No records")

    def test_show_with_data(self):
        self.ui.current_table.add(name='Alice')
        with patch('builtins.print') as mock_print:
            self.ui._show_all_records()
            assert mock_print.called


class TestFindById:
    def setup_method(self):
        self.db = Database()
        self.ui = ConsoleInterface(self.db)
        self.db.create_table('Users', {'name': str})
        self.ui.current_table = self.db.get_table('Users')

    def test_find_success(self):
        self.ui.current_table.add(name='Alice')
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print') as mock_print:
                self.ui._find_by_id()
                assert mock_print.called

    def test_find_invalid_format(self):
        with patch('builtins.input', return_value='abc'):
            with patch('builtins.print') as mock_print:
                self.ui._find_by_id()
                mock_print.assert_any_call("Invalid id format")


class TestFilter:
    def setup_method(self):
        self.db = Database()
        self.ui = ConsoleInterface(self.db)
        self.db.create_table('Users', {'name': str, 'age': int})
        self.ui.current_table = self.db.get_table('Users')

    def test_filter_with_data(self):
        self.ui.current_table.add(name='Alice', age=30)
        with patch('builtins.input', side_effect=['Alice', '30']):
            with patch('builtins.print') as mock_print:
                self.ui._filter_records()
                assert mock_print.called

    def test_filter_no_results(self):
        with patch('builtins.input', side_effect=['Bob', '']):
            with patch('builtins.print') as mock_print:
                self.ui._filter_records()
                mock_print.assert_any_call("No records found")


class TestUpdate:
    def setup_method(self):
        self.db = Database()
        self.ui = ConsoleInterface(self.db)
        self.db.create_table('Users', {'name': str, 'age': int})
        self.ui.current_table = self.db.get_table('Users')

    def test_update_success(self):
        self.ui.current_table.add(name='Alice', age=30)
        with patch('builtins.input', side_effect=['1', 'Bob', '', '31']):
            with patch('builtins.print') as mock_print:
                self.ui._update_record()
                assert mock_print.called

    def test_update_invalid_id(self):
        with patch('builtins.input', return_value='abc'):
            with patch('builtins.print') as mock_print:
                self.ui._update_record()
                mock_print.assert_any_call("Invalid id format")


class TestDelete:
    def setup_method(self):
        self.db = Database()
        self.ui = ConsoleInterface(self.db)
        self.db.create_table('Users', {'name': str})
        self.ui.current_table = self.db.get_table('Users')

    def test_delete_success(self):
        self.ui.current_table.add(name='Alice')
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print') as mock_print:
                self.ui._delete_record()
                assert len(self.ui.current_table.records) == 0

    def test_delete_invalid_id(self):
        with patch('builtins.input', return_value='abc'):
            with patch('builtins.print') as mock_print:
                self.ui._delete_record()
                mock_print.assert_any_call("Invalid id format")


class TestSort:
    def setup_method(self):
        self.db = Database()
        self.ui = ConsoleInterface(self.db)
        self.db.create_table('Users', {'name': str, 'age': int})
        self.ui.current_table = self.db.get_table('Users')

    def test_sort_asc(self):
        self.ui.current_table.add(name='Bob', age=30)
        self.ui.current_table.add(name='Alice', age=25)
        with patch('builtins.input', side_effect=['age', 'asc']):
            with patch('builtins.print') as mock_print:
                self.ui._sort_records()
                assert mock_print.called

    def test_sort_desc(self):
        self.ui.current_table.add(name='Bob', age=30)
        self.ui.current_table.add(name='Alice', age=25)
        with patch('builtins.input', side_effect=['age', 'desc']):
            with patch('builtins.print'):
                self.ui._sort_records()
        records = self.ui.current_table.sort('age', reverse=True)
        assert records[0]['age'] == 30

    def test_sort_invalid_field(self):
        self.ui.current_table.add(name='Alice', age=25)
        with patch('builtins.input', side_effect=['invalid', 'asc']):
            with patch('builtins.print') as mock_print:
                self.ui._sort_records()
                assert mock_print.called


class TestMenus:
    def setup_method(self):
        self.db = Database()
        self.ui = ConsoleInterface(self.db)

    def test_show_main_menu_exit(self):
        with patch('builtins.input', return_value='0'):
            with patch('builtins.print'):
                with pytest.raises(SystemExit):
                    self.ui._show_main_menu()

    def test_show_main_menu_invalid(self):
        with patch('builtins.input', side_effect=['9']):
            with patch('builtins.print') as mock_print:
                self.ui._show_main_menu()
                mock_print.assert_any_call("Invalid input")

    def test_show_main_menu_create(self):
        with patch('builtins.input', side_effect=['1', 'Users', 'done']):
            with patch('builtins.print'):
                self.ui._show_main_menu()

    def test_show_main_menu_select(self):
        self.db.create_table('Users', {'name': str})
        with patch('builtins.input', side_effect=['2', '1']):
            with patch('builtins.print'):
                self.ui._show_main_menu()

    def test_show_main_menu_list(self):
        with patch('builtins.input', side_effect=['3']):
            with patch('builtins.print'):
                self.ui._show_main_menu()

    def test_show_table_menu_back(self):
        self.db.create_table('Users', {'name': str})
        self.ui.current_table = self.db.get_table('Users')
        with patch('builtins.input', return_value='0'):
            with patch('builtins.print'):
                self.ui._show_table_menu()
        assert self.ui.current_table is None

    def test_show_table_menu_add(self):
        self.db.create_table('Users', {'name': str})
        self.ui.current_table = self.db.get_table('Users')
        with patch('builtins.input', side_effect=['1', 'Alice']):
            with patch('builtins.print'):
                self.ui._show_table_menu()

    def test_show_table_menu_show(self):
        self.db.create_table('Users', {'name': str})
        self.ui.current_table = self.db.get_table('Users')
        with patch('builtins.input', return_value='2'):
            with patch('builtins.print'):
                self.ui._show_table_menu()

    def test_show_table_menu_invalid(self):
        self.db.create_table('Users', {'name': str})
        self.ui.current_table = self.db.get_table('Users')
        with patch('builtins.input', return_value='99'):
            with patch('builtins.print') as mock_print:
                self.ui._show_table_menu()
                mock_print.assert_any_call("Invalid input")


class TestRun:
    def test_run_and_exit(self):
        db = Database()
        ui = ConsoleInterface(db)
        with patch('builtins.input', side_effect=['0', '0']):
            with patch('builtins.print'):
                with pytest.raises(SystemExit):
                    ui.run()