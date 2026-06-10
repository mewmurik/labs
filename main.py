from database import Database
from exceptions import RecordNotFoundError, InvalidInputError, DatabaseError


def print_main_menu():
    print("\n" + "=" * 50)
    print("   In-Memory Database")
    print("=" * 50)
    print("1. Создать новую таблицу")
    print("2. Выбрать таблицу для работы")
    print("3. Показать все таблицы")
    print("0. Выход")
    print("-" * 50)


def print_table_menu(table_name, schema):
    print("\n" + "=" * 50)
    print(f"   Работа с таблицей: {table_name}")
    print(f"   Схема: {schema}")
    print("=" * 50)
    print("1. Добавить запись")
    print("2. Показать все записи")
    print("3. Найти запись по ID")
    print("4. Найти записи по фильтру")
    print("5. Обновить запись")
    print("6. Удалить запись")
    print("0. Вернуться к выбору таблиц")
    print("-" * 50)

def create_table_interactive(db):
    """Интерактивное создание новой таблицы"""
    print("\n--- Создание новой таблицы ---")
    name = input("Введите имя таблицы: ").strip()
    
    if not name:
        print("Имя таблицы не может быть пустым")
        return None
    
    print("Введите поля таблицы в формате: имя_поле:тип")
    print("Доступные типы: str, int, float")
    print("Пример: name:str, group:str, grade:float")
    print("(Введите 'готово' для завершения)")
    
    schema = {}
    while True:
        field_input = input("Поле: ").strip()
        if field_input.lower() == 'готово':
            break
        if ':' not in field_input:
            print("Неверный формат. Используйте имя:тип")
            continue
        
        field_name, field_type = field_input.split(':', 1)
        field_name = field_name.strip()
        field_type = field_type.strip().lower()
        
        if field_type == 'str':
            schema[field_name] = str
        elif field_type == 'int':
            schema[field_name] = int
        elif field_type == 'float':
            schema[field_name] = float
        else:
            print(f"Неизвестный тип: {field_type}")
            continue
        
        print(f"Добавлено поле: {field_name} ({field_type})")
    
    if not schema:
        print("Таблица должна содержать хотя бы одно поле")
        return None
    
    # Добавляем поле id автоматически (оно всегда есть)
    print("Поле 'id' (автоинкремент) будет добавлено автоматически")
    
    try:
        table = db.create_table(name, schema)
        print(f"Таблица '{name}' успешно создана!")
        return table
    except DatabaseError as e:
        print(e)
        return None

def get_table_interactive(db):
    """Выбор существующей таблицы"""
    if not db.tables:
        print("Нет созданных таблиц. Сначала создайте таблицу.")
        return None
    
    print("\nДоступные таблицы:")
    for i, table_name in enumerate(db.tables.keys(), 1):
        print(f"  {i}. {table_name}")
    
    try:
        choice = int(input("Выберите таблицу по номеру: "))
        table_name = list(db.tables.keys())[choice - 1]
        return db.get_table(table_name)
    except (ValueError, IndexError):
        print("Неверный выбор")
        return None

def work_with_table(table):
    """Работа с выбранной таблицей"""
    while True:
        print_table_menu(table.name, table.schema)
        choice = input("Выберите действие: ").strip()
        
        try:
            if choice == '1':
                kwargs = {}
                for field, field_type in table.schema.items():
                    value = input(f"Введите {field} ({field_type.__name__}): ").strip()
                    if field_type == int:
                        kwargs[field] = int(value)
                    elif field_type == float:
                        kwargs[field] = float(value)
                    else:
                        kwargs[field] = value
                record_id = table.add(**kwargs)
                print(f"Запись добавлена с id={record_id}")

            elif choice == '2':
                records = table.get()
                if not records:
                    print("Нет записей")
                else:
                    print(f"\nВсе записи в таблице '{table.name}':")
                    for r in records:
                        print(f"  {r}")

            elif choice == '3':
                record_id = int(input("Введите id: "))
                record = table.get(record_id)
                print(f"  {record}")

            elif choice == '4':
                print("Фильтрация (оставьте пустым, если не нужно)")
                filters = {}
                for field in table.schema.keys():
                    value = input(f"{field}: ").strip()
                    if value:
                        field_type = table.schema[field]
                        if field_type == int:
                            filters[field] = int(value)
                        elif field_type == float:
                            filters[field] = float(value)
                        else:
                            filters[field] = value
                
                records = table.get(filters=filters)
                if not records:
                    print("Записи не найдены")
                else:
                    for r in records:
                        print(f"  {r}")

            elif choice == '5':
                record_id = int(input("Введите id для обновления: "))
                print("Оставьте пустым, если поле не меняется")
                updates = {}
                for field in table.schema.keys():
                    value = input(f"Новое значение {field}: ").strip()
                    if value:
                        field_type = table.schema[field]
                        if field_type == int:
                            updates[field] = int(value)
                        elif field_type == float:
                            updates[field] = float(value)
                        else:
                            updates[field] = value
                
                table.update(record_id, **updates)
                print(f"Запись id={record_id} обновлена")

            elif choice == '6':
                record_id = int(input("Введите id для удаления: "))
                table.delete(record_id)
                print(f"Запись id={record_id} удалена")

            elif choice == '0':
                break

            else:
                print("Неверный ввод. Попробуйте снова.")

        except RecordNotFoundError as e:
            print(f"Ошибка: {e}")
        except InvalidInputError as e:
            print(f"Ошибка ввода: {e}")
        except ValueError:
            print("Ошибка: неверный формат числа")
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")


def main():
    db = Database()
    try:
        db.create_table('Students', {
            'name': str,
            'group': str,
            'grade': float
        })
        print("Таблица 'Students' создана по умолчанию")
    except DatabaseError:
        pass
    
    print("Добро пожаловать в In-Memory Database!")
    
    while True:
        print_main_menu()
        choice = input("Выберите действие: ").strip()
        
        if choice == '1':
            create_table_interactive(db)
        
        elif choice == '2':
            table = get_table_interactive(db)
            if table:
                work_with_table(table)
        
        elif choice == '3':
            if not db.tables:
                print("Нет созданных таблиц")
            else:
                print("\nСуществующие таблицы:")
                for table_name, table in db.tables.items():
                    print(f" {table_name}: {table.schema}")
        
        elif choice == '0':
            print("До свидания!")
            break
        
        else:
            print("Неверный ввод. Попробуйте снова.")

if __name__ == "__main__":
    main()