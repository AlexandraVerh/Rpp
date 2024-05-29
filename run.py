from aiogram import Bot, Dispatcher, types
from rgz.handlers.registration import register_handlers_registration
from rgz.handlers.operations import register_handlers_operations
import asyncio
import os

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
bot = Bot(token=bot_token)
dp = Dispatcher(bot=bot)

register_handlers_registration(dp)
register_handlers_operations(dp)

if __name__ == '__main__':
    async def main():
        await dp.start_polling(bot)

    asyncio.run(main())
