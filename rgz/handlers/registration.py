from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.command import Command
from rgz.data.database import is_user_registered, add_user

class RegistrationForm(StatesGroup):
    waiting_for_name = State()

def register_handlers_registration(dp: Dispatcher):
    @dp.message(Command('reg'))
    async def start_registration(message: types.Message, state: FSMContext):
        if not is_user_registered(message.chat.id):
            await message.answer('Введите свой логин:')
            await state.set_state(RegistrationForm.waiting_for_name)
        else:
            await message.answer('Вы уже зарегистрированы.')

    @dp.message(RegistrationForm.waiting_for_name)
    async def process_name(message: types.Message, state: FSMContext):
        if message.text.isalpha():
            data = await state.get_data()
            data['name'] = message.text
            data['chat_id'] = message.chat.id
            user_id = add_user(data['name'], data['chat_id'])
            await state.set_state(None)  # Reset the state machine
            await message.answer('Вы успешно зарегистрированы.')
        else:
            await message.answer('Имя должно содержать только буквы.')

