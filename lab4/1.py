from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

import os
import logging

#Получение токена из переменных окружения
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

#Создание бота с токеном, который выдал при регистрации бота
bot = Bot(token=bot_token)
#Инициализация диспетчера команд
dp = Dispatcher(bot, storage=MemoryStorage())

#Форма, которая хранит информацию о ползователе
class Form(StatesGroup):
    name = State()#поле, в котором хранится имя текущего пользователя

#Обработчик команды /start
@dp.message_handler(commands=['start'])
async def process_start_command(message: Message):
    await Form.name.set()
    await message.reply("Как тебя зовут?")

#Обработка введенного имени
@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state:FSMContext):
    await state.update_data(name=message.text)
    user_data = await state.get_data()
    await message.reply("Привет, " + user_data['name'])

#Точка входа в приложение
if __name__ == '__main__':
    #Инициализация системы логирования
    logging.basicConfig(level=logging.INFO)
    #Подключение системы логирования к боту
    dp.middleware.setup(LoggingMiddleware())
    #Запуск обработчиков команд
    executor.start_polling(dp, skip_updates=True)

