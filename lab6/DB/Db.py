from aiogram import types, Dispatcher, Bot, executor # Импорт классов для работы с ботом и диспетчером
from aiogram.fsm.storage.memory import MemoryStorage # Импорт класса для хранения состояний FSM в памяти
import os #предоставляет функции для взаимодействия с операционной системой.
import psycopg2 #который предоставляет адаптер для подключения к базе данных PostgreSQL.


# Получение токена из переменных окружения
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

# Создание бота с токеном
bot = Bot(token=bot_token)

storage = MemoryStorage()#Создает экземпляр класса MemoryStorage для хранения состояний машины состояний в памяти.
dp = Dispatcher(bot=bot, storage=storage)#оздает экземпляр класса Dispatcher с переданными экземплярами Bot и MemoryStorage.
 #Настройки базы данных
conn = psycopg2.connect(# Создает подключение к базе данных PostgreSQL
    host="127.0.0.1",
    database="postgres",
    user="postgres",
    password="postgres"
)

cur = conn.cursor()#Создает курсор для выполнения SQL-запросов к базе данных.

cur.execute(#Выполняет SQL-запрос на создание таблицы
    "CREATE TABLE IF NOT EXISTS currencies ("
    "id SERIAL PRIMARY KEY,"
    "currency_name VARCHAR(50) NOT NULL,"
    "rate FLOAT NOT NULL)"
)

conn.commit()#Фиксирует изменения в базе данных.
conn.close()