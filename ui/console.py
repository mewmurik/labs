from typing import Optional
from models.file_database import FileDatabase
from models.database import Database as InMemoryDatabase
from models.exceptions import RecordNotFoundError, InvalidInputError, DatabaseError
from storage.json_storage import JSONStorage
from storage.csv_storage import CSVStorage
from storage.indexed_storage import IndexedStorage


class ConsoleInterface:
    def __init__(self):
        self.db = None
        self.current_table = None
        self.mode = "memory"

    def run(self):
        print("Welcome to In-Memory/File Database")
        self._select_mode()

        while True:
            if self.current_table is None:
                self._show_main_menu()
            else:
                self._show_table_menu()

    def _select_mode(self):
        print("\nSelect storage mode:")
        print("1. In-Memory (data lost after exit)")
        print("2. File (JSON) - data saved to disk")
        print("3. File (CSV) - data saved to disk")
        print("4. File (JSON with indexes) - fast search")

        choice = input("Choose mode: ").strip()

        if choice == '1':
            self.db = InMemoryDatabase()
            self.mode = "memory"
            print("In-Memory mode selected")
        elif choice == '2':
            storage = JSONStorage("json_data")
            self.db = FileDatabase(storage)
            self.mode = "json"
            print("JSON file mode selected")
        elif choice == '3':
            storage = CSVStorage("csv_data")
            self.db = FileDatabase(storage)
            self.mode = "csv"
            print("CSV file mode selected")
        elif choice == '4':
            storage = IndexedStorage("indexed_data")
            self.db = FileDatabase(storage)
            self.mode = "indexed"
            print("Indexed JSON mode selected")
        else:
            self.db = InMemoryDatabase()
            self.mode = "memory"
            print("Invalid choice. In-Memory mode selected")

        try:
            self.db.create_table('Students', {
                'name': str,
                'group': str,
                'grade': float
            })
            print("Table 'Students' created by default")
        except DatabaseError:
            pass

    def _show_main_menu(self):
        print("\n" + "=" * 50)
        print(f"   Database ({self.mode} mode)")
        print("=" * 50)
        print("1. Create new table")
        print("2. Select table")
        print("3. Show all tables")
        print("0. Exit")
        print("-" * 50)

        choice = input("Choose action: ").strip()

        if choice == '1':
            self._create_table()
        elif choice == '2':
            self._select_table()
        elif choice == '3':
            self._list_tables()
        elif choice == '0':
            print("Goodbye")
            exit(0)
        else:
            print("Invalid input")

    def _show_table_menu(self):
        print(f"\n" + "=" * 50)
        print(f"   Table: {self.current_table.name}")
        print(f"   Schema: {self.current_table.schema}")
        print("=" * 50)
        print("1. Add record")
        print("2. Show all records")
        print("3. Find by ID")
        print("4. Filter records")
        print("5. Update record")
        print("6. Delete record")
        print("7. Sort records")
        if self.mode == "indexed":
            print("8. Create index")
            print("9. Search by index")
        print("0. Back to tables")
        print("-" * 50)

        choice = input("Choose action: ").strip()

        try:
            if choice == '1':
                self._add_record()
            elif choice == '2':
                self._show_all_records()
            elif choice == '3':
                self._find_by_id()
            elif choice == '4':
                self._filter_records()
            elif choice == '5':
                self._update_record()
            elif choice == '6':
                self._delete_record()
            elif choice == '7':
                self._sort_records()
            elif choice == '8' and self.mode == "indexed":
                self._create_index()
            elif choice == '9' and self.mode == "indexed":
                self._search_by_index()
            elif choice == '0':
                self.current_table = None
            else:
                print("Invalid input")
        except Exception as e:
            print(f"Error: {e}")

    def _create_table(self):
        print("\n--- Create new table ---")
        name = input("Table name: ").strip()

        if not name:
            print("Table name cannot be empty")
            return

        print("Enter fields as name:type")
        print("Available types: str, int, float")
        print("Example: name:str, age:int")
        print("Type 'done' to finish")

        schema = {}
        while True:
            field_input = input("Field: ").strip()
            if field_input.lower() == 'done':
                break
            if ':' not in field_input:
                print("Invalid format. Use name:type")
                continue

            field_name, field_type = field_input.split(':', 1)
            field_name = field_name.strip()
            field_type = field_type.strip().lower()

            type_map = {'str': str, 'int': int, 'float': float}
            if field_type not in type_map:
                print(f"Unknown type: {field_type}")
                continue

            schema[field_name] = type_map[field_type]
            print(f"Added field: {field_name} ({field_type})")

        if not schema:
            print("Table must have at least one field")
            return

        try:
            self.db.create_table(name, schema)
            print(f"Table '{name}' created")
        except DatabaseError as e:
            print(f"Error: {e}")

    def _select_table(self):
        tables = self.db.list_tables()
        if not tables:
            print("No tables created")
            return

        print("\nAvailable tables:")
        for i, table_name in enumerate(tables, 1):
            print(f"  {i}. {table_name}")

        try:
            choice = int(input("Select table by number: "))
            if 1 <= choice <= len(tables):
                self.current_table = self.db.get_table(tables[choice - 1])
                print(f"Selected table: {self.current_table.name}")
            else:
                print("Invalid choice")
        except ValueError:
            print("Invalid choice")

    def _list_tables(self):
        tables = self.db.list_tables()
        if not tables:
            print("No tables created")
        else:
            print("\nExisting tables:")
            for table_name in tables:
                print(f"  {table_name}")

    def _add_record(self):
        kwargs = {}
        for field, field_type in self.current_table.schema.items():
            value = input(f"Enter {field} ({field_type.__name__}): ").strip()
            if field_type is int:
                kwargs[field] = int(value)
            elif field_type is float:
                kwargs[field] = float(value)
            else:
                kwargs[field] = value
        record_id = self.current_table.add(**kwargs)
        print(f"Record added with id={record_id}")

    def _show_all_records(self):
        records = self.current_table.get_all()
        if not records:
            print("No records")
        else:
            print(f"\nAll records in table '{self.current_table.name}':")
            for r in records:
                print(f"  {r}")

    def _find_by_id(self):
        try:
            record_id = int(input("Enter id: "))
            record = self.current_table.get(record_id)
            print(f"  {record}")
        except ValueError:
            print("Invalid id format")

    def _filter_records(self):
        print("Filtering (leave empty to skip)")
        filters = {}
        for field in self.current_table.schema.keys():
            value = input(f"{field}: ").strip()
            if value:
                field_type = self.current_table.schema[field]
                if field_type is int:
                    filters[field] = int(value)
                elif field_type is float:
                    filters[field] = float(value)
                else:
                    filters[field] = value

        records = self.current_table.get(filters=filters)
        if not records:
            print("No records found")
        else:
            for r in records:
                print(f"  {r}")

    def _update_record(self):
        try:
            record_id = int(input("Enter id to update: "))
            print("Leave empty to skip")
            updates = {}
            for field in self.current_table.schema.keys():
                value = input(f"New {field}: ").strip()
                if value:
                    field_type = self.current_table.schema[field]
                    if field_type is int:
                        updates[field] = int(value)
                    elif field_type is float:
                        updates[field] = float(value)
                    else:
                        updates[field] = value

            self.current_table.update(record_id, **updates)
            print(f"Record id={record_id} updated")
        except ValueError:
            print("Invalid id format")

    def _delete_record(self):
        try:
            record_id = int(input("Enter id to delete: "))
            self.current_table.delete(record_id)
            print(f"Record id={record_id} deleted")
        except ValueError:
            print("Invalid id format")

    def _sort_records(self):
        available_fields = list(self.current_table.schema.keys())
        print(f"Available fields: id, {', '.join(available_fields)}")
        field = input("Enter field to sort by: ").strip()
        order = input("Order (asc/desc): ").strip().lower()

        reverse = order == 'desc'

        try:
            sorted_records = self.current_table.sort(field, reverse)
            print(f"\nSorted records by '{field}':")
            for r in sorted_records:
                print(f"  {r}")
        except InvalidInputError as e:
            print(f"Error: {e}")

    def _create_index(self):
        if self.mode != "indexed":
            print("Indexes only available in indexed mode")
            return
        available_fields = list(self.current_table.schema.keys())
        print(f"Available fields: {', '.join(available_fields)}")
        field = input("Enter field to index: ").strip()
        if field not in available_fields:
            print(f"Field '{field}' does not exist")
            return
        storage = self.db.storage
        if hasattr(storage, 'create_index'):
            storage.create_index(self.current_table.name, field)
            print(f"Index created on field '{field}'")
        else:
            print("Indexing not supported")

    def _search_by_index(self):
        if self.mode != "indexed":
            print("Indexes only available in indexed mode")
            return
        available_fields = list(self.current_table.schema.keys())
        print(f"Available fields: {', '.join(available_fields)}")
        field = input("Enter field to search: ").strip()
        if field not in available_fields:
            print(f"Field '{field}' does not exist")
            return
        value = input(f"Enter value for {field}: ").strip()
        storage = self.db.storage
        if hasattr(storage, 'get_by_index'):
            ids = storage.get_by_index(self.current_table.name, field, value)
            if ids:
                print(f"Records found with {field}={value}: {ids}")
                for record_id in ids:
                    try:
                        record = self.current_table.get(record_id)
                        print(f"  {record}")
                    except RecordNotFoundError:
                        pass
            else:
                print("No records found")
        else:
            print("Indexing not supported")