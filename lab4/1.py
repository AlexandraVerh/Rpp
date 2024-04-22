from aiogram.dispatcher import FSMContext  # Импорт класса для работы с FSM (finite state machine)
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # Импорт класса для хранения состояний FSM в памяти
from aiogram.dispatcher.filters.state import State, StatesGroup  # Импорт классов для определения состояний FSM и группы состояний
from aiogram.types import Message  # Импорт класса Message для работы с сообщениями
from aiogram import Bot, Dispatcher, types  # Импорт классов для работы с ботом и диспетчером
from aiogram.contrib.middlewares.logging import LoggingMiddleware  # Импорт middleware для логирования
from aiogram.utils import executor  # Импорт функции executor для запуска бота
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import logging  # Импорт модуля логирования
import os  # Импорт модуля для работы с переменными окружения
import asyncio
import asyncpg


# Получение API токена бота из переменных окружения
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

# Создание экземпляра бота с использованием API токена
bot = Bot(token=bot_token)
# Инициализация диспетчера с указанием хранилища в памяти
dp = Dispatcher(bot, storage=MemoryStorage())

# Обработчик команды /admin_id для добавления в бд меня как администратора
@dp.message_handler(commands=['admin_id'])
async def show_user_id(message: types.Message):
    user_id = message.from_user.id
    await message.reply(f"Ваш user_id: {user_id}")

# Функция для проверки администраторских прав пользователя
async def is_admin(user_id):
    conn = await asyncpg.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1', port=5432)
    try:
        query = "SELECT 1 FROM admins WHERE chat_id = $1"
        result = await conn.fetchrow(query, str(user_id))
        if result:
            return True
        else:
            return False
    finally:
        await conn.close()

async def save_currency_to_db(currency_name, rate):
    conn = await asyncpg.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1', port=5432)
    try:
        query = "INSERT INTO currencies (currency_name, rate) VALUES ($1, $2)"
        await conn.execute(query, currency_name, rate)
    finally:
        await conn.close()

# Объявление класса Form, который содержит состояния FSM для информации о пользователе и конвертации валют
class Form(StatesGroup):
    name = State()  # Определение состояния для хранения имени текущего пользователя
    currency_name = State()  # Определение состояния для хранения названия валюты
    currency_rate = State()  # Определение состояния для хранения курса валюты к рублю
    convert_currency_name = State()  # Определение состояния для хранения названия валюты для конвертации
    convert_currency_amount = State()  # Определение состояния для хранения суммы для конвертации
    delete_currency_name = State()  # Определение состояния для удаления названия валюты
    change_currency_name = State()  # Определение состояния для изменения названия валюты
    new_currency_rate = State()  # Определение состояния для нового курса валюты

# Обработчик команды /manage_currency для управления валютами
@dp.message_handler(commands=['manage_currency'])
async def manage_currency_command(message: types.Message):
    user_id = message.from_user.id
    if not await is_admin(user_id):
        await message.reply("Нет доступа к команде.")
    else:
        keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        buttons = [
            KeyboardButton("Добавить валюту"),
            KeyboardButton("Удалить валюту"),
            KeyboardButton("Изменить курс валюты")
        ]
        keyboard.add(*buttons)
        await message.reply("Выберите действие:", reply_markup=keyboard)

# Обработчик кнопки "Добавить валюту"
@dp.message_handler(lambda message: message.text == "Добавить валюту")
async def add_currency_step1(message: types.Message):
    await message.reply("Введите название валюты:")
    await Form.currency_name.set()

# Обработчик ввода названия валюты
@dp.message_handler(state=Form.currency_name)
async def add_currency_step2(message: types.Message, state: FSMContext):
    currency_name = message.text

    # Проверяем, что валюта уже существует
    if await is_currency_exists(currency_name):
        await message.reply("Данная валюта уже существует.")
        await state.finish()
        return

    await state.update_data(currency_name=currency_name)
    await message.reply("Введите курс к рублю:")
    await Form.currency_rate.set()

# Обработчик ввода курса валюты
@dp.message_handler(state=Form.currency_rate)
async def add_currency_step3(message: types.Message, state: FSMContext):
    currency_rate = float(message.text)
    user_data = await state.get_data()
    currency_name = user_data['currency_name']

    # Сохраняем валюту в базу данных
    await save_currency_to_db(currency_name, currency_rate)

    await message.reply(f"Валюта {currency_name} успешно добавлена с курсом {currency_rate}")

    await state.finish()

# Функция для проверки наличия валюты в базе данных
async def is_currency_exists(currency_name):
    conn = await asyncpg.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1', port=5432)
    try:
        query = "SELECT currency_name FROM currencies WHERE currency_name = $1"
        result = await conn.fetch(query, currency_name)
        return bool(result)
    finally:
        await conn.close()

# Функция для сохранения валюты в базу данных
async def save_currency_to_db(currency_name, currency_rate):
    conn = await asyncpg.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1', port=5432)
    try:
        query = "INSERT INTO currencies (currency_name, rate) VALUES ($1, $2)"
        await conn.execute(query, currency_name, currency_rate)
    finally:
        await conn.close()


# Обработчик кнопки "Удалить валюту"
@dp.message_handler(lambda message: message.text == "Удалить валюту")
async def delete_currency_step1(message: types.Message):
    await message.reply("Введите название валюты, которую вы хотите удалить:")
    await Form.delete_currency_name.set()

# Обработчик ввода названия валюты для удаления
@dp.message_handler(state=Form.delete_currency_name)
async def delete_currency_step2(message: types.Message, state: FSMContext):
    currency_name = message.text

    # Проверяем, что валюта существует в базе данных
    if await is_currency_exists(currency_name):
        # Удаляем валюту из базы данных
        await delete_currency_from_db(currency_name)
        await message.reply(f"Валюта {currency_name} успешно удалена.")
    else:
        await message.reply(f"Валюта {currency_name} не найдена в базе данных.")

    await state.finish()

# Функция для удаления валюты из базы данных
async def delete_currency_from_db(currency_name):
    conn = await asyncpg.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1', port=5432)
    try:
        query = "DELETE FROM currencies WHERE currency_name = $1"
        await conn.execute(query, currency_name)
    finally:
        await conn.close()

# Функция для проверки наличия валюты в базе данных
async def is_currency_exists(currency_name):
    conn = await asyncpg.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1', port=5432)
    try:
        query = "SELECT currency_name FROM currencies WHERE currency_name = $1"
        result = await conn.fetch(query, currency_name)
        return bool(result)
    finally:
        await conn.close()

# Обработчик кнопки "Изменить курс валюты"
@dp.message_handler(lambda message: message.text == "Изменить курс валюты")
async def change_currency_step1(message: types.Message):
    await message.reply("Введите название валюты, курс которой вы хотите изменить:")
    await Form.change_currency_name.set()

# Обработчик ввода названия валюты для изменения курса
@dp.message_handler(state=Form.change_currency_name)
async def change_currency_step2(message: types.Message, state: FSMContext):
    currency_name = message.text

    # Проверяем, что валюта существует в базе данных
    if await is_currency_exists(currency_name):
        await state.update_data(currency_name=currency_name)
        await message.reply("Введите новый курс к рублю:")
        await Form.new_currency_rate.set()
    else:
        await message.reply(f"Валюта {currency_name} не найдена в базе данных.")
        await state.finish()

# Обработчик ввода нового курса валюты
@dp.message_handler(state=Form.new_currency_rate)
async def change_currency_step3(message: types.Message, state: FSMContext):
    new_currency_rate = float(message.text)
    user_data = await state.get_data()
    currency_name = user_data['currency_name']

    # Обновляем курс валюты в базе данных
    await update_currency_rate_in_db(currency_name, new_currency_rate)

    await message.reply(f"Курс валюты {currency_name} успешно изменен на {new_currency_rate}.")

    await state.finish()

# Функция для обновления курса валюты в базе данных
async def update_currency_rate_in_db(currency_name, new_currency_rate):
    conn = await asyncpg.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1', port=5432)
    try:
        query = "UPDATE currencies SET rate = $1 WHERE currency_name = $2"
        await conn.execute(query, new_currency_rate, currency_name)
    finally:
        await conn.close()



# Обработчик команды /start для начала работы с ботом
@dp.message_handler(commands=['start'])
async def process_start_command(message: Message):
    await Form.currency_name.set()  # Установка текущего состояния на ввод названия валюты
    await message.reply("Привет! Я бот для конвертации валют. Для сохранения курса валюты используй команду /save_currency.")

# Обработчик команды /save_currency для сохранения курса новой валюты
@dp.message_handler(commands=['save_currency'])
async def save_currency_command(message: types.Message):
    await Form.currency_name.set()  # Установка текущего состояния на ввод названия валюты
    await message.reply("Введите название валюты:")

# Обработка введенного названия валюты для сохранения курса
@dp.message_handler(state=Form.currency_name)
async def process_currency_name_for_saving(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['currency_name'] = message.text

    await Form.currency_rate.set()  # Установка состояния на ввод курса валюты к рублю
    await message.reply("Введите курс валюты к рублю:")

# Обработка введенного курса валюты для сохранения
@dp.message_handler(state=Form.currency_rate)
async def process_currency_rate_for_saving(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        currency_name = data['currency_name']
        currency_rate = message.text

    # Сохраняем информацию о валюте и курсе в базу данных
    await save_currency_to_db(currency_name, currency_rate)

    await message.reply(f"Информация о валюте {currency_name} успешно сохранена. Курс к рублю: {currency_rate}. Чтобы сделать конвертацию используй команду /convert")

    await state.finish()

# Функция для получения курса валюты из базы данных
async def get_currency_rate(currency_name):
    conn = await asyncpg.connect(database='postgres', user='postgres', password='postgres', host='127.0.0.1', port=5432)
    try:
        query = "SELECT rate FROM currencies WHERE currency_name = $1"
        rate = await conn.fetchval(query, currency_name)
        return rate
    finally:
        await conn.close()

# Обработчик команды /convert для начала процесса конвертации валюты
@dp.message_handler(commands=['convert'])
async def convert_currency_command(message: types.Message):
    await Form.convert_currency_name.set()  # Установка текущего состояния на ввод названия валюты для конвертации
    await message.reply("Введите название валюты, которую вы хотите конвертировать в рубли:")

# Обработка введенного названия валюты для конвертации
@dp.message_handler(state=Form.convert_currency_name)
async def process_convert_currency_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['convert_currency_name'] = message.text

    await Form.convert_currency_amount.set()  # Установка состояния для ввода суммы для конвертации
    await message.reply("Теперь введите сумму в выбранной валюте для конвертации в рубли:")

# Обработка введенной суммы для конвертации
@dp.message_handler(state=Form.convert_currency_amount)
async def process_convert_currency_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        convert_currency_name = data['convert_currency_name']
        convert_currency_amount = float(message.text)

        # Получаем курс выбранной валюты из базы данных
        currency_rate = await get_currency_rate(convert_currency_name)

        if currency_rate is not None:
            converted_amount = convert_currency_amount * currency_rate
            await message.reply(f"{convert_currency_amount} {convert_currency_name} равно {converted_amount} рублей.")
        else:
            await message.reply(f"Извините, курс для валюты {convert_currency_name} не найден в базе данных.")

        await state.finish()

# Точка входа в приложение, запуск обработки сообщений
if __name__ == '__main__':
    # Инициализация системы логирования с уровнем INFO
    logging.basicConfig(level=logging.INFO)
    # Подключение системы логирования к диспетчеру бота
    dp.middleware.setup(LoggingMiddleware())
    # Запуск обработки входящих сообщений бота
    executor.start_polling(dp, skip_updates=True)