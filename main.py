from database import Database
from exceptions import RecordNotFoundError, InvalidInputError, DatabaseError


def print_menu():
    print("\n" + "=" * 50)
    print("   In-Memory Database")
    print("=" * 50)
    print("1. Добавить запись")
    print("2. Показать все записи")
    print("3. Найти запись по ID")
    print("4. Найти записи по фильтру")
    print("5. Обновить запись")
    print("6. Удалить запись")
    print("0. Выход")
    print("-" * 50)


def main():
    # Инициализация базы данных
    db = Database()

    # Создаём таблицу Students
    students_table = db.create_table('Students', {
        'name': str,
        'group': str,
        'grade': float
    })

    print("Добро пожаловать в In-Memory Database!")
    print("Создана таблица 'Students' с полями: name(str), group(str), grade(float)")

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()

        try:
            if choice == '1':
                name = input("Введите имя: ")
                group = input("Введите группу: ")
                grade = float(input("Введите средний балл: "))
                record_id = students_table.add(name=name, group=group, grade=grade)
                print(f"Запись добавлена с id={record_id}")

            elif choice == '2':
                records = students_table.get()
                if not records:
                    print("Нет записей")
                else:
                    print("\nВсе записи:")
                    for r in records:
                        print(f"  id={r['id']}, name={r['name']}, group={r['group']}, grade={r['grade']}")

            elif choice == '3':
                record_id = int(input("Введите id: "))
                record = students_table.get(record_id)
                print(f"id={record['id']}, name={record['name']}, group={record['group']}, grade={record['grade']}")

            elif choice == '4':
                print("Фильтрация (оставьте пустым, если не нужно)")
                name = input("Имя: ").strip() or None
                group = input("Группа: ").strip() or None
                grade_str = input("Средний балл: ").strip()
                grade = float(grade_str) if grade_str else None

                filters = {}
                if name:
                    filters['name'] = name
                if group:
                    filters['group'] = group
                if grade is not None:
                    filters['grade'] = grade

                records = students_table.get(filters=filters)
                if not records:
                    print("Записи не найдены")
                else:
                    for r in records:
                        print(f"  id={r['id']}, name={r['name']}, group={r['group']}, grade={r['grade']}")

            elif choice == '5':
                record_id = int(input("Введите id для обновления: "))
                print("Оставьте пустым, если поле не меняется")
                name = input("Новое имя: ").strip()
                group = input("Новая группа: ").strip()
                grade_str = input("Новый средний балл: ").strip()

                updates = {}
                if name:
                    updates['name'] = name
                if group:
                    updates['group'] = group
                if grade_str:
                    updates['grade'] = float(grade_str)

                students_table.update(record_id, **updates)
                print(f"Запись id={record_id} обновлена")

            elif choice == '6':
                record_id = int(input("Введите id для удаления: "))
                students_table.delete(record_id)
                print(f"Запись id={record_id} удалена")

            elif choice == '0':
                print("До свидания!")
                break

            else:
                print("Неверный ввод. Попробуйте снова.")

        except RecordNotFoundError as e:
            print(f"Ошибка: {e}")
        except InvalidInputError as e:
            print(f"Ошибка ввода: {e}")
        except DatabaseError as e:
            print(f"Ошибка базы данных: {e}")
        except ValueError:
            print("Ошибка: неверный формат числа")
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")

if __name__ == "__main__":
    main()