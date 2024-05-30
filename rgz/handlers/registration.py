# Импорт необходимых модулей из библиотеки aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.command import Command
from rgz.data.database import is_user_registered, add_user  # Импорт функций из другого модуля

# Определение класса-группы состояний RegistrationForm
class RegistrationForm(StatesGroup):
    waiting_for_name = State()  # Определение состояния waiting_for_name

# Функция для регистрации обработчиков регистрации
def register_handlers_registration(dp: Dispatcher):
    # Обработчик команды '/reg'
    @dp.message(Command('reg'))
    async def start_registration(message: types.Message, state: FSMContext):
        if not is_user_registered(message.chat.id):  # Проверка, зарегистрирован ли уже пользователь
            await message.answer('Введите свой логин:')  # Отправка сообщения о запросе логина
            await state.set_state(RegistrationForm.waiting_for_name)  # Установка состояния waiting_for_name
        else:
            await message.answer('Вы уже зарегистрированы.')  # Отправка сообщения о уже существующей регистрации

    # Обработчик ожидания имени пользователя
    @dp.message(RegistrationForm.waiting_for_name)
    async def process_name(message: types.Message, state: FSMContext):
        if message.text.isalpha():  # Проверка, содержит ли имя только буквы
            data = await state.get_data()  # Получение данных из состояния
            data['name'] = message.text  # Сохранение имени пользователя в данных
            data['chat_id'] = message.chat.id  # Сохранение chat_id пользователя в данных
            user_id = add_user(data['name'], data['chat_id'])  # Добавление пользователя в базу данных
            await state.set_state(None)  # Сброс состояния
            await message.answer('Вы успешно зарегистрированы.')  # Отправка сообщения о успешной регистрации
        else:
            await message.answer('Имя должно содержать только буквы.')  # Отправка сообщения об ошибке в имени
