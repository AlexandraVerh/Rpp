# Импорт библиотеки psycopg2, которая используется для работы с PostgreSQL
import psycopg2

# Функция для подключения к базе данных PostgreSQL
def connect():
    conn = psycopg2.connect(
        dbname='rgz',  # Название базы данных
        user='postgres',  # Пользователь базы данных
        password='postgres',  # Пароль от пользователя
        host='127.0.0.1',  # Хост базы данных
        port=5432  # Порт подключения
    )
    return conn

# Функция для проверки зарегистрирован ли пользователь по chat_id в таблице users
def is_user_registered(chat_id):
    conn = connect()  # Устанавливаем соединение с базой данных
    cursor = conn.cursor()  # Создаем объект курсора для выполнения SQL-запросов
    cursor.execute('SELECT * FROM users WHERE chat_id = %s', (chat_id,))  # Выполняем SQL-запрос
    result = cursor.fetchone()  # Получаем результат запроса
    conn.close()  # Закрываем соединение с базой данных
    return result is not None  # Возвращаем True, если пользователь зарегистрирован, иначе False

# Функция для добавления нового пользователя в таблицу users
def add_user(name, chat_id):
    conn = connect()  # Устанавливаем соединение с базой данных
    cursor = conn.cursor()  # Создаем объект курсора для выполнения SQL-запросов
    cursor.execute('INSERT INTO users (name, chat_id) VALUES (%s, %s) RETURNING id', (name, chat_id))  # Выполняем SQL-запрос
    user_id = cursor.fetchone()[0]  # Получаем ID нового пользователя
    conn.commit()  # Фиксируем транзакцию
    conn.close()  # Закрываем соединение с базой данных
    return user_id  # Возвращаем ID нового пользователя

# Функция для добавления операции в таблицу operations
def add_operation(chat_id, date, sum, type_operation):
    conn = connect()  # Устанавливаем соединение с базой данных
    cursor = conn.cursor()  # Создаем объект курсора для выполнения SQL-запросов
    cursor.execute('INSERT INTO operations (date, sum, chat_id, type_operation) VALUES (%s, %s, %s, %s)', (date, sum, chat_id, type_operation))  # Выполняем SQL-запрос для добавления операции
    conn.commit()  # Фиксируем транзакцию
    conn.close()  # Закрываем соединение с базой данных

# Функция для получения операций пользователя по его chat_id
def get_operations_by_user(chat_id):
    conn = connect()  # Устанавливаем соединение с базой данных
    cursor = conn.cursor()  # Создаем объект курсора для выполнения SQL-запросов
    cursor.execute("SELECT * FROM operations WHERE chat_id = %s", (chat_id,))  # Выполняем SQL-запрос для получения операций пользователя
    operations = cursor.fetchall()  # Получаем все операции пользователя
    conn.close()  # Закрываем соединение с базой данных
    return operations  # Возвращаем список операций

# Функция для обновления суммы операции по её ID
def update_operation(operation_id, new_sum):
    conn = connect()  # Устанавливаем соединение с базой данных
    cursor = conn.cursor()  # Создаем объект курсора для выполнения SQL-запросов
    cursor.execute('UPDATE operations SET sum = %s WHERE id = %s', (new_sum, operation_id))  # Выполняем SQL-запрос для обновления суммы операции
    conn.commit()  # Фиксируем транзакцию
    conn.close()  # Закрываем соединение с базой данных

