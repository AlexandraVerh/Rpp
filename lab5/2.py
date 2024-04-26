from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import types, Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
import os
import psycopg2
import asyncio
import logging
import sys
from decimal import Decimal

# Настройки бота

# Получение токена из переменных окружения
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

# Создание бота с токеном
bot = Bot(token=bot_token)

storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

# Настройки базы данных
conn = psycopg2.connect(
    host="127.0.0.1",
    database="postgres",
    user="postgres",
    password="postgres"
)

cur = conn.cursor()

cur.execute(
    "CREATE TABLE IF NOT EXISTS currencies ("
    "id SERIAL PRIMARY KEY,"
    "currency_name VARCHAR(50) NOT NULL,"
    "rate FLOAT NOT NULL)"
)

cur.execute(
    "CREATE TABLE IF NOT EXISTS admins ("
    "id SERIAL PRIMARY KEY,"
    "chat_id VARCHAR NOT NULL)"
)

conn.commit()

# Состояния для машины состояний
class ManageCurrency(StatesGroup):
    waiting_for_currency_name = State()
    waiting_for_currency_rate = State()
    waiting_for_currency_name_delete = State()
    waiting_for_currency_name_change = State()
    waiting_for_currency_rate_change = State()
    waiting_for_currency_name_convert = State()
    waiting_for_currency_rate_convert = State()

async def is_user_admin(user_id: int) -> bool:
    cur.execute("SELECT * FROM admins WHERE chat_id = %s", (str(user_id),))
    return bool(cur.fetchone())

# Добавление администратора в таблицу admins
async def add_admin(chat_id: int):
    cur.execute("INSERT INTO admins (chat_id) VALUES (%s) RETURNING id", (str(chat_id),))
    conn.commit()

# Хэндлер для команды /manage_currency
@dp.message(Command('manage_currency'))
async def manage_currency_command(message: types.Message):
    if await is_user_admin(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, keyboard=[])
        button1 = types.KeyboardButton(text="Добавить валюту")
        button2 = types.KeyboardButton(text="Удалить валюту")
        button3 = types.KeyboardButton(text="Изменить курс валюты")
        markup.keyboard.append([button1, button2, button3])
        await message.answer("Выберите действие", reply_markup=markup)
    else:
        await message.answer("Нет доступа к команде")


# Хэндлер для нажатия на кнопку "Добавить валюту"
@dp.message(lambda message: message.text == "Добавить валюту")
async def add_currency_command(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(ManageCurrency.waiting_for_currency_name)

# Хэндлер для обработки ввода пользователем названия валюты
@dp.message(ManageCurrency.waiting_for_currency_name)
async def process_currency_name(message: types.Message, state: FSMContext):
    data = await state.get_data()

    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (message.text,))
    if cur.fetchone():
        await message.answer(f"Валюта {message.text} уже существует.")
        await state.set_state(None)
    else:
        await state.update_data(currency_name=message.text)
        await state.set_state(ManageCurrency.waiting_for_currency_rate)
        await message.answer(f'Введите курс валюты {message.text} к рублю:')


# Хэндлер для обработки ввода пользователем курса к рублю
@dp.message(ManageCurrency.waiting_for_currency_rate)
async def process_currency_rate(message: types.Message, state: FSMContext):
    data = await state.get_data()
    currency_name = data.get('currency_name')
    currency_rate = float(message.text)

    cur.execute("INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)", (currency_name, currency_rate))
    conn.commit()
    await message.answer(f"Валюта {currency_name} с курсом {currency_rate} успешно добавлена!")
    await state.set_state(None)


# Хэндлер для нажатия на кнопку "Удалить валюту"
@dp.message(lambda message: message.text == "Удалить валюту")
async def delete_currency_command(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты, которую хотите удалить:")
    await state.set_state(ManageCurrency.waiting_for_currency_name_delete)


# Обработчик для удаления существующей валюты
@dp.message(ManageCurrency.waiting_for_currency_name_delete)
async def process_delete_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text

    cur.execute("DELETE FROM currencies WHERE currency_name = %s", (currency_name,))
    conn.commit()

    await message.answer(f"Валюта {currency_name} успешно удалена.")
    await state.set_state(None)


# Хэндлер для кнопки "Изменить курс валюты"
@dp.message(lambda message: message.text == "Изменить курс валюты")
async def change_currency_rate_command(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(ManageCurrency.waiting_for_currency_name_change)


# Хэндлер для обработки выбранной валюты для обновления курса
@dp.message(ManageCurrency.waiting_for_currency_name_change)
async def process_currency_name_change(message: types.Message, state: FSMContext):
    data = await state.get_data()
    currency_name = data.get('currency_name')

    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (message.text,))
    currency_data = cur.fetchone()

    if not currency_data:
        await message.answer(f"Валюты {message.text} не существует. Попробуйте снова.")
        await state.set_state(None)
    else:
        await state.update_data(currency_name=message.text)
        await state.set_state(ManageCurrency.waiting_for_currency_rate_change)
        await message.answer(f'Введите новый курс для валюты {message.text} к рублю:')

# Хэндлер для обработки ввода нового курса валюты к рублю
@dp.message(ManageCurrency.waiting_for_currency_rate_change)
async def process_currency_rate_change(message: types.Message, state: FSMContext):
    data = await state.get_data()
    currency_name = data.get('currency_name')
    new_rate = float(message.text)

    # Обновление курса валюты в базе данных
    cur.execute("UPDATE currencies SET rate = %s WHERE currency_name = %s", (new_rate, currency_name))
    conn.commit()

    await message.answer(f"Курс валюты {currency_name} успешно изменен на {new_rate}.")
    await state.set_state(None)


# Хэндлер для команды /get_currencies
@dp.message(Command('get_currencies'))
async def get_currencies_command(message: types.Message):
    cur.execute("SELECT * FROM currencies")
    currencies = cur.fetchall()

    if not currencies:
        await message.answer("Нет сохраненных валют")
    else:
        for currency in currencies:
            await message.answer(f"{currency[1]}: {currency[2]} руб.")

# Хэндлер для команды /start
@dp.message(Command('start'))
async def start_command(message: types.Message):
    # Добавление администратора с id 349231719 в таблицу admins при старте бота
    if not await is_user_admin(910772816):
        await add_admin(910772816)

    if await is_user_admin(message.from_user.id):
        button1 = types.KeyboardButton(text="/start")
        button2 = types.KeyboardButton(text="/manage_currency")
        button3 = types.KeyboardButton(text="/get_currencies")
        button4 = types.KeyboardButton(text="/convert")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4, keyboard=[[button1, button2, button3, button4]])
        await message.answer("Выберите команду из доступных:\n"
                    "/manage_currency - открыть панель администратора\n"
                    "/get_currencies - посмотреть список валют\n"
                    "/convert - конвертировать валюту", reply_markup=markup)
    else:
        button1 = types.KeyboardButton(text="/start")
        button2 = types.KeyboardButton(text="/get_currencies")
        button3 = types.KeyboardButton(text="/convert")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, keyboard=[[button1, button2, button3]])
        await message.answer("Выберите команду из доступных:\n"
                             " /get_currencies - посмотреть список валют\n"
                             " /convert - конвертировать валюту", reply_markup=markup)

# Хэндлер для команды /convert
@dp.message(Command('convert'))
async def convert_command(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(ManageCurrency.waiting_for_currency_name_convert)


# Обработчик для ввода названия валюты для конвертации
@dp.message(ManageCurrency.waiting_for_currency_name_convert)
async def process_currency_name_convert(message: types.Message, state: FSMContext):
    currency_name = message.text

    await state.update_data(currency_name=currency_name)
    await state.set_state(ManageCurrency.waiting_for_currency_rate_convert)
    await message.answer("Введите сумму для конвертации:")


# Обработчик для ввода суммы для конвертации
@dp.message(ManageCurrency.waiting_for_currency_rate_convert)
async def process_currency_rate_convert(message: types.Message, state: FSMContext):
    data = await state.get_data()
    currency_name = data.get('currency_name')
    conversion_rate = float(message.text)

    cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency_name,))
    rate = cur.fetchone()

    if rate:
        rate_value = Decimal(rate[0]).quantize(Decimal('0.01'))  # Convert Decimal to float
        converted_amount = conversion_rate * float(rate_value)
        await message.answer(f"{conversion_rate} {currency_name} = {converted_amount} рублей.")
    else:
        await message.answer(f"Ошибка: Валюта {currency_name} не найдена.")

    await state.set_state(None)


# Запуск бота
async def main() -> None:
    try:
        await dp.start_polling(bot)
    finally:
        conn.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())