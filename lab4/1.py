from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import logging
import os

# Получение токена из переменных окружения
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

# Создание бота с токеном
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())

# Форма, которая хранит информацию о пользователе
class Form(StatesGroup):
    name = State()  # поле, в котором хранится имя текущего пользователя
    currency_name = State()
    currency_rate = State()
    convert_currency_name = State()
    convert_currency_amount = State()

# Объявление списка для хранения данных о курсах валют
currency_list = []

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def process_start_command(message: Message):
    await Form.currency_name.set()
    await message.reply("Привет! Я бот для конвертации валют. Для сохранения курса валюты используй команду /save_currency.")

# Обработчик команды /save_currency
@dp.message_handler(commands=['save_currency'])
async def save_currency_command(message: types.Message):
    await Form.currency_name.set()
    await message.reply("Введите название валюты:")

# Обработка введенного названия валюты для сохранения курса
@dp.message_handler(state=Form.currency_name)
async def process_currency_name_for_saving(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['currency_name'] = message.text

    await Form.currency_rate.set()
    await message.reply("Введите курс валюты к рублю:")

# Обработка введенного курса валюты для сохранения
@dp.message_handler(state=Form.currency_rate)
async def process_currency_rate_for_saving(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['currency_rate'] = message.text

    user_data = await state.get_data()
    currency_name = user_data['currency_name']
    currency_rate = user_data['currency_rate']

    # Сохранение информации о валюте в словарь или базу данных
    currency_list.append({currency_name: currency_rate})

    await message.reply(f"Информация о валюте {currency_name} успешно сохранена. Курс к рублю: {currency_rate}. Чтобы сделать конвертацию используй команду  /convert")

    await state.finish()

# Обработчик команды /convert
@dp.message_handler(commands=['convert'])
async def convert_currency_command(message: types.Message):
    await Form.convert_currency_name.set()
    await message.reply("Введите название валюты, которую вы хотите конвертировать в рубли:")

# Обработка введенного названия валюты для конвертации
@dp.message_handler(state=Form.convert_currency_name)
async def process_convert_currency_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['convert_currency_name'] = message.text

    await Form.convert_currency_amount.set()
    await message.reply("Теперь введите сумму в выбранной валюте для конвертации в рубли:")

# Обработка введенной суммы для конвертации
@dp.message_handler(state=Form.convert_currency_amount)
async def process_convert_currency_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_data = await state.get_data()
        convert_currency_name = data['convert_currency_name']
        convert_currency_amount = float(message.text)

        # Поиск курса выбранной валюты в списке
        currency_rate = None
        for item in currency_list:
            if convert_currency_name in item.keys():
                currency_rate = item[convert_currency_name]
                break

        if currency_rate is not None:
            converted_amount = convert_currency_amount * float(currency_rate)
            await message.reply(f"{convert_currency_amount} {convert_currency_name} равно {converted_amount} рублей.")
        else:
            await message.reply(f"Извините, курс для валюты {convert_currency_name} не найден.")

        await state.finish()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    dp.middleware.setup(LoggingMiddleware())
    executor.start_polling(dp, skip_updates=True)