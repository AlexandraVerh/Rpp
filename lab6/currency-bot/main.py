from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import types, Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault
import requests
import os
import psycopg2
import asyncio
import logging
import sys

# Настройки бота
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
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

# Состояния для машины состояний
class ManageCurrency(StatesGroup):
    waiting_for_currency_name = State()
    waiting_for_currency_rate = State()
    waiting_for_currency_name_delete = State()
    waiting_for_currency_name_change = State()
    waiting_for_currency_rate_change = State()
    waiting_for_currency_name_convert = State()
    waiting_for_currency_amount_convert = State()

# Список команд с описанием
commands = [
    BotCommand(command="/start", description="Помощь"),
    BotCommand(command="/manage_currency", description="редактирование валют"),
    BotCommand(command="/get_currencies", description="список валют"),
    BotCommand(command="/convert", description="конвертировать")
]

# Хэндлер для команды /manage_currency
@dp.message(Command('manage_currency'))
async def manage_currency_command(message: types.Message):
    # Получение роли пользователя
    response = requests.get(f'http://127.0.0.1:5003/get_admin/{message.chat.id}')
    if response.status_code == 200:
        role = response.json().get('admin')
        if role:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, keyboard=[])
            button1 = types.KeyboardButton(text="Добавить валюту")
            button2 = types.KeyboardButton(text="Удалить валюту")
            button3 = types.KeyboardButton(text="Изменить курс валюты")
            markup.keyboard.append([button1, button2, button3])
            await message.answer("Выберите действие", reply_markup=markup)
        else:
            await message.answer("У вас недостаточно прав для выполнения этой команды")
    else:
        await message.answer("Ошибка при получении роли")

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

    # Отправка запроса на добавление валюты в микросервис currencymanager
    response = requests.post(f'http://127.0.0.1:5001/load', json={
        "currency_name": currency_name,
        "rate": currency_rate
    })
    if response.status_code == 200:
        await message.answer(f"Валюта {currency_name} с курсом {currency_rate} успешно добавлена!")
    else:
        await message.answer(f"Ошибка при добавлении валюты {currency_name}")

    await state.set_state(None)

# Хэндлер для нажатия на кнопку "Удалить валюту"
@dp.message(lambda message: message.text == "Удалить валюту")
async def delete_currency_command(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(ManageCurrency.waiting_for_currency_name_delete)

# Хэндлер для обработки ввода пользователем названия валюты для удаления
@dp.message(ManageCurrency.waiting_for_currency_name_delete)
async def process_currency_name_delete(message: types.Message, state: FSMContext):
    data = await state.get_data()

    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (message.text,))
    if not cur.fetchone():
        await message.answer(f"Валюта {message.text} не найдена.")
        await state.set_state(None)
    else:
        await state.update_data(currency_name=message.text)

        # Отправка запроса на удаление валюты в микросервис currencymanager
        # Отправка запроса на удаление валюты в микросервис currencymanager
        response = requests.post(f'http://127.0.0.1:5001/delete', json={
            "currency_name": message.text
        })

        if response.status_code == 200:
            await message.answer(f"Валюта {message.text} успешно удалена!")
        else:
            await message.answer(f"Ошибка при удалении валюты {message.text}")

        await state.set_state(None)

@dp.message(lambda message: message.text == "Изменить курс валюты")
async def change_currency_command(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(ManageCurrency.waiting_for_currency_name_change)

@dp.message(ManageCurrency.waiting_for_currency_name_change)
async def process_currency_name_change(message: types.Message, state: FSMContext):
    data = await state.get_data()

    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (message.text,))
    if not cur.fetchone():
        await message.answer(f"Валюта {message.text} не найдена.")
        await state.set_state(None)
    else:
        await state.update_data(currency_name=message.text)
        await state.set_state(ManageCurrency.waiting_for_currency_rate_change)
        await message.answer(f'Введите новый курс валюты {message.text} к рублю:')

@dp.message(ManageCurrency.waiting_for_currency_rate_change)
async def process_currency_rate_change(message: types.Message, state: FSMContext):
    data = await state.get_data()
    currency_name = data.get('currency_name')
    new_currency_rate = float(message.text)

    # Отправка запроса на обновление курса валюты в микросервис currencymanager
    response = requests.post(f'http://127.0.0.1:5001/update_currency', json={
        "currency_name": currency_name,
        "new_rate": new_currency_rate
    })
    if response.status_code == 200:
        await message.answer(f"Курс валюты {currency_name} успешно обновлен!")
    else:
        await message.answer(f"Ошибка при обновлении курса валюты {currency_name}")

    await state.set_state(None)


@dp.message(Command('get_currencies'))
async def get_currencies_command(message: types.Message):
    # Отправка запроса на получение всех валют в микросервис data-manager
    response = requests.get(f'http://127.0.0.1:5002/currencies')
    if response.status_code == 200:
        currencies = response.json().get('currencies')
        if not currencies:
            await message.answer("Нет сохраненных валют.")
        else:
            await message.answer("\n".join(currencies))
    else:
        await message.answer("Ошибка при получении валют.")


# Хэндлер для команды /convert
@dp.message(Command('convert'))
async def convert_command(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(ManageCurrency.waiting_for_currency_name_convert)


# Хэндлер для обработки ввода пользователем названия валюты для конвертации
@dp.message(ManageCurrency.waiting_for_currency_name_convert)
async def process_currency_name_convert(message: types.Message, state: FSMContext):
    data = await state.get_data()

    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (message.text,))
    if not cur.fetchone():
        await message.answer(f"Валюта {message.text} не найдена.")
        await state.set_state(None)
    else:
        await state.update_data(currency_name=message.text)
        await state.set_state(ManageCurrency.waiting_for_currency_amount_convert)
        await message.answer(f'Введите сумму в валюте {message.text}:')

# Хэндлер для обработки ввода пользователем суммы для конвертации
@dp.message(ManageCurrency.waiting_for_currency_amount_convert)
async def process_currency_amount_convert(message: types.Message, state: FSMContext):
    data = await state.get_data()
    currency_name = data.get('currency_name')
    currency_amount = float(message.text)

    # Отправка запроса на получение курса валюты в микросервис currencymanager
    response = requests.get(f'http://127.0.0.1:5002/convert?currency_name={currency_name}&amount={currency_amount}')
    if response.status_code == 200:
        converted_amount = response.json().get('converted_amount')
        await message.answer(f"Сумма в рублях: {converted_amount}")
    else:
        await message.answer(f"Ошибка при получении курса валюты {currency_name}")

    await state.set_state(None)



# Хэндлер для команды /start
@dp.message(Command('start'))
async def start_command(message: types.Message):
    # Создание настраиваемой клавиатуры с кнопками, расположенными в 3 столбца
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, keyboard=[])
    button1 = types.KeyboardButton(text="/start")
    button2 = types.KeyboardButton(text="/manage_currency")
    button3 = types.KeyboardButton(text="/get_currencies")
    button4 = types.KeyboardButton(text="/convert")
    markup.keyboard.append([button1, button2, button3, button4])

    # Отправка сообщения пользователю с информацией о доступных командах и настраиваемой клавиатурой
    await message.answer("Выберите команду из доступных:\n"
                         " /manage_currency - редактирование валют\n"
                         " /get_currencies - список валют\n"
                         " /convert - конвертировать валюту", reply_markup=markup)


# Запуск бота

async def main() -> None:
    try:
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
        await dp.start_polling(bot, skip_updates=True)
    finally:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())




