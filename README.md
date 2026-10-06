markdown
# In-Memory Database (File Storage version)

Расширенная версия in-memory базы данных с поддержкой файлового хранения в форматах JSON и CSV, а также индексацией для быстрого поиска.

## Структура проекта
pioa-m6o-122bv-25/
¦
+-- models/ # Модели данных
¦ +-- init.py
¦ +-- database.py # In-memory Database и Table
¦ +-- file_database.py # Файловая Database и Table
¦ L-- exceptions.py # Пользовательские исключения
¦
+-- ui/ # Пользовательский интерфейс
¦ +-- init.py
¦ L-- console.py # Консольный интерфейс (класс ConsoleInterface)
¦
+-- storage/ # Хранилища данных
¦ +-- init.py
¦ +-- base.py # Абстрактный класс StorageBackend
¦ +-- json_storage.py # JSON файловое хранилище
¦ +-- csv_storage.py # CSV файловое хранилище
¦ L-- indexed_storage.py # JSON с индексацией
¦
+-- tests/ # Автоматические тесты
¦ +-- init.py
¦ +-- test_database.py # Тесты in-memory (20 тестов)
¦ L-- test_file_database.py # Тесты файлового хранения (7 тестов)
¦
+-- main.py # Точка входа
L-- README.md

text

## Функциональность

### Основная (3 балла)
- Создание нескольких таблиц
- CRUD операции (Create, Read, Update, Delete)
- Фильтрация записей по одному или нескольким полям
- Сортировка записей по выбранному полю (возрастание/убывание)
- Файловое хранение в формате JSON
- Обработка ошибок (некорректный ввод, отсутствие записей)

### Дополнительная (4 балла)
- CSV формат хранения данных

### Дополнительная (5 баллов)
- Индексация данных для ускорения поиска
- Поиск по индексированным полям

## Режимы работы

При запуске программы можно выбрать один из четырёх режимов:

| Режим | Описание | Сохранение данных |
|-------|----------|-------------------|
| 1. In-Memory | Данные хранятся только в оперативной памяти | Нет |
| 2. File (JSON) | Хранение в JSON файлах | Да |
| 3. File (CSV) | Хранение в CSV файлах | Да |
| 4. Indexed JSON | JSON с индексацией для быстрого поиска | Да |

## Инструкция по запуску

### Требования
- Python 3.13 или выше
- Установленный pytest (для запуска тестов)

### Установка pytest (для тестов)
```bash
pip install pytest
Запуск программы
bash
python main.py
Пример работы
Главное меню
text
==================================================
   Database (json mode)
==================================================
1. Create new table
2. Select table
3. Show all tables
0. Exit
Меню работы с таблицей
text
==================================================
   Table: Students
   Schema: {'name': <class 'str'>, 'group': <class 'str'>, 'grade': <class 'float'>}
==================================================
1. Add record
2. Show all records
3. Find by ID
4. Filter records
5. Update record
6. Delete record
7. Sort records
8. Create index (только в indexed режиме)
9. Search by index (только в indexed режиме)
0. Back to tables
Пример добавления записи
text
Enter name (str): Иван Петров
Enter group (str): М6О-122БВ-25
Enter grade (float): 4.5
Record added with id=1
Пример вывода всех записей
text
All records in table 'Students':
  {'id': 1, 'name': 'Иван Петров', 'group': 'М6О-122БВ-25', 'grade': 4.5}
  {'id': 2, 'name': 'Мария Иванова', 'group': 'М6О-122БВ-25', 'grade': 4.8}
Структура файлов данных
JSON режим (папка json_data/)
{table_name}.json - записи таблицы

{table_name}_id.json - счётчик ID

{table_name}_schema.json - схема таблицы

CSV режим (папка csv_data/)
{table_name}.csv - записи таблицы

{table_name}_id.json - счётчик ID

{table_name}_schema.json - схема таблицы

Индексированный режим (папка indexed_data/)
{table_name}.json - записи таблицы

{table_name}_id.json - счётчик ID

{table_name}_schema.json - схема таблицы

{table_name}_idx_{field}.json - индекс по полю