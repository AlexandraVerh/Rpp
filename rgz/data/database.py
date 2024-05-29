import psycopg2

def connect():
    conn = psycopg2.connect(
        dbname='rgz',
        user='postgres',
        password='postgres',
        host='127.0.0.1',
        port=5432
    )
    return conn

def is_user_registered(chat_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE chat_id = %s', (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def add_user(name, chat_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, chat_id) VALUES (%s, %s) RETURNING id', (name, chat_id))
    user_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return user_id

def add_operation(chat_id, date, sum, type_operation):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO operations (date, sum, chat_id, type_operation) VALUES (%s, %s, %s, %s)', (date, sum, chat_id, type_operation))
    conn.commit()
    conn.close()

def get_operations_by_user(chat_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operations WHERE chat_id = %s", (chat_id,))
    operations = cursor.fetchall()
    conn.close()
    return operations

