# Импорт необходимых модулей из библиотеки aiogram
from aiogram import Bot, Dispatcher
from rgz.handlers.registration import register_handlers_registration
from rgz.handlers.operations import register_handlers_operations

# Импорт модуля asyncio для асинхронного выполнения кода
import asyncio
import os

# Получение токена Telegram бота из переменных окружения
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

# Инициализация экземпляра класса Bot с использованием полученного токена
bot = Bot(token=bot_token)

# Инициализация экземпляра класса Dispatcher с использованием созданного экземпляра класса Bot
dp = Dispatcher(bot=bot)

# Регистрация обработчиков для раздела "регистрация"
register_handlers_registration(dp)

# Регистрация обработчиков для раздела "операции"
register_handlers_operations(dp)

# Если код запускается непосредственно (а не импортирован как модуль)
if __name__ == '__main__':
    # Определение асинхронной функции main
    async def main():
        # Запуск бесконечного цикла получения сообщений от Telegram бота
        await dp.start_polling(bot)

    # Запуск асинхронной функции main с помощью asyncio
    asyncio.run(main())
