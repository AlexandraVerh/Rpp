from rgz.data.database import add_operation, is_user_registered
from datetime import datetime
from aiogram import types, Router, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
import requests
from rgz.data.database import get_operations_by_user
import datetime
from decimal import Decimal

router = Router()

class AddOperation(StatesGroup):
    type_operation = State()
    sum = State()
    date = State()

@router.message(Command('add_operation'))
async def add_operation_start(message: types.Message, state: FSMContext):
    if not is_user_registered(message.chat.id):
        await message.answer("Вы не зарегистрированы. Используйте команду /reg для регистрации.")
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[types.KeyboardButton(text="РАСХОД"), types.KeyboardButton(text="ДОХОД")]])
    await message.answer("Выберите тип операции: \nРАСХОД \nДОХОД", reply_markup=keyboard)
    await state.set_state(AddOperation.type_operation)

@router.message(AddOperation.type_operation, filters.StateFilter(AddOperation.type_operation))
async def type_operation_handler(message: types.Message, state: FSMContext):
    if message.text not in ["РАСХОД", "ДОХОД"]:
        await message.answer("Неверный тип операции. Попробуйте еще раз.")
        return

    await message.answer("Введите сумму операции в рублях:")
    await state.update_data(type_operation=message.text)
    await state.set_state(AddOperation.sum)

@router.message(AddOperation.sum, filters.StateFilter(AddOperation.sum))
async def sum_handler(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Неверная сумма. Попробуйте еще раз.")
        return

    await message.answer("Введите дату операции в формате ДД.ММ.ГГГГ:")
    await state.update_data(sum=int(message.text))
    await state.set_state(AddOperation.date)

@router.message(AddOperation.date, filters.StateFilter(AddOperation.date))
async def date_handler(message: types.Message, state: FSMContext):
    try:
        date = datetime.datetime.strptime(message.text, '%d.%m.%Y')

    except ValueError:
        await message.answer("Неверная дата. Попробуйте еще раз.")
        return

    data = await state.get_data()
    add_operation(message.chat.id, date, data["sum"], data["type_operation"])
    await message.answer("Операция успешно добавлена.")
    await state.clear()

class ViewOperations(StatesGroup):
    currency = State()

@router.message(Command('operations'))
async def view_operations(message: types.Message, state: FSMContext):
    if not is_user_registered(message.chat.id):
        await message.answer("Вы не зарегистрированы. Используйте команду /reg для регистрации.")
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[types.KeyboardButton(text="RUB"), types.KeyboardButton(text="EUR"), types.KeyboardButton(text="USD")]])
    await message.answer("Выберите валюту, в которой хотите получить информацию по операциям:", reply_markup=keyboard)
    await state.set_state(ViewOperations.currency)

@router.message(ViewOperations.currency, filters.StateFilter(ViewOperations.currency))
async def view_operations_currency(message: types.Message, state: FSMContext):
    currency = message.text.upper()
    if currency not in ["RUB", "EUR", "USD"]:
        await message.answer("Неверная валюта. Попробуйте еще раз.")
        return

    # Получаем актуальный курс, если выбрана валюта отличная от RUB
    rate = Decimal(1.0)  # преобразуем в Decimal для корректного умножения
    if currency != "RUB":
        try:
            response = requests.get(f"http://195.58.54.159:8000/rate?currency={currency}")
            response.raise_for_status()
            if response.status_code == 200:
                rate = Decimal(response.json()["rate"])  # преобразуем в Decimal для корректного умножения
            else:
                await message.answer("Произошла ошибка при получении курса валют. Попробуйте позже.")
                return
        except requests.exceptions.RequestException as e:
            await message.answer("Произошла ошибка при получении курса валют. Попробуйте позже.")
            return

    # Получаем все операции пользователя из базы данных
    operations = get_operations_by_user(message.chat.id)

    # Выводим информацию по каждой операции в выбранной валюте
    for operation in operations:
        operation_date = operation[1].strftime("%d.%m.%Y")
        operation_sum = operation[2] / rate if currency != "RUB" else operation[2]
        type_operation = operation[4]
        operation_sum_formatted = "{:.2f}".format(operation_sum)
        await message.answer(f"{operation_date} - {type_operation}: {operation_sum_formatted} {currency}")

    await state.clear()

def register_handlers_operations(dp):
    dp.include_router(router)