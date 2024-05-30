# Импорт функций из модуля rgz.data.database
from rgz.data.database import add_operation, is_user_registered, update_operation
# Импорт модуля datetime для работы с датами
from datetime import datetime
# Импорт необходимых классов и функций из библиотеки aiogram
from aiogram import types, Router, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
# Импорт класса Command из aiogram.filters для работы с командами
from aiogram.filters import Command
# Импорт модуля requests для выполнения HTTP-запросов
import requests
# Импорт функции get_operations_by_user из модуля rgz.data.database
from rgz.data.database import get_operations_by_user
# Импорт модуля datetime (из стандартной библиотеки Python)
import datetime
# Импорт класса Decimal из модуля decimal для работы с десятичными числами
from decimal import Decimal


# Создание экземпляра класса Router для роутинга сообщений
router = Router()

# Определение класса состояний AddOperation, наследуемого от StatesGroup
class AddOperation(StatesGroup):
    type_operation = State()  # Определение состояния type_operation
    sum = State()  # Определение состояния sum
    date = State()  # Определение состояния date

# Обработчик команды '/add_operation'
@router.message(Command('add_operation'))
async def add_operation_start(message: types.Message, state: FSMContext):
    if not is_user_registered(message.chat.id):  # Проверка, зарегистрирован ли пользователь
        await message.answer("Вы не зарегистрированы. Используйте команду /reg для регистрации.")
        return

    # Создание клавиатуры для выбора типа операции
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         keyboard=[[types.KeyboardButton(text="РАСХОД"),
                                                    types.KeyboardButton(text="ДОХОД")]])
    await message.answer("Выберите тип операции: \nРАСХОД \nДОХОД", reply_markup=keyboard)
    await state.set_state(AddOperation.type_operation)  # Установка состояния type_operation

# Обработчик сообщения при установленном состоянии type_operation
@router.message(AddOperation.type_operation, filters.StateFilter(AddOperation.type_operation))
async def type_operation_handler(message: types.Message, state: FSMContext):
    if message.text not in ["РАСХОД", "ДОХОД"]:  # Проверка выбранного типа операции
        await message.answer("Неверный тип операции. Попробуйте еще раз.")
        return

    await message.answer("Введите сумму операции в рублях:")
    await state.update_data(type_operation=message.text)  # Обновление данных в состоянии
    await state.set_state(AddOperation.sum)  # Установка следующего состояния на sum

# Обработчик сообщения при установленном состоянии sum
@router.message(AddOperation.sum, filters.StateFilter(AddOperation.sum))
async def sum_handler(message: types.Message, state: FSMContext):
    if not message.text.isdigit():  # Проверка введенной суммы
        await message.answer("Неверная сумма. Попробуйте еще раз.")
        return

    await message.answer("Введите дату операции в формате ДД.ММ.ГГГГ:")
    await state.update_data(sum=int(message.text))  # Обновление данных в состоянии
    await state.set_state(AddOperation.date)  # Установка следующего состояния на date

# Обработчик сообщения при установленном состоянии date
@router.message(AddOperation.date, filters.StateFilter(AddOperation.date))
async def date_handler(message: types.Message, state: FSMContext):
    try:
        date = datetime.datetime.strptime(message.text, '%d.%m.%Y')  # Преобразование введенной даты в формат datetime

    except ValueError:
        await message.answer("Неверная дата. Попробуйте еще раз.")
        return

    data = await state.get_data()  # Получение данных из состояния
    add_operation(message.chat.id, date, data["sum"], data["type_operation"])  # Добавление операции в базу данных
    await message.answer("Операция успешно добавлена.")  # Отправка сообщения об успешном добавлении операции
    await state.clear()  # Сброс состояния

# Определение состояний для просмотра операций
class ViewOperations(StatesGroup):
    currency = State()

# Обработчик сообщения при получении команды '/operations'
@router.message(Command('operations'))
async def view_operations(message: types.Message, state: FSMContext):
    if not is_user_registered(message.chat.id):  # Проверка, зарегистрирован ли пользователь
        await message.answer("Вы не зарегистрированы. Используйте команду /reg для регистрации.")
        return

    # Создание клавиатуры для выбора валюты
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [types.KeyboardButton(text="RUB"), types.KeyboardButton(text="EUR"), types.KeyboardButton(text="USD")]])
    await message.answer("Выберите валюту, в которой хотите получить информацию по операциям:",
                         reply_markup=keyboard)  # Отправка сообщения с клавиатурой выбора валюты
    await state.set_state(ViewOperations.currency)  # Установка состояния на currency для обработки выбора валюты

# Обработчик сообщения с выбранной валютой для просмотра операций
@router.message(ViewOperations.currency, filters.StateFilter(ViewOperations.currency))
async def view_operations_currency(message: types.Message, state: FSMContext):
    currency = message.text.upper()  # Получаем выбранную валюту и преобразуем в верхний регистр
    if currency not in ["RUB", "EUR", "USD"]:  # Проверка на корректность введенной валюты
        await message.answer("Неверная валюта. Попробуйте еще раз.")
        return

    rate = Decimal(1.0)  # Установка начального курса в 1.0
    if currency != "RUB":  # Если выбрана другая валюта, получаем актуальный курс
        try:
            response = requests.get(f"http://195.58.54.159:8000/rate?currency={currency}")  # Отправка запроса для получения курса
            response.raise_for_status()
            if response.status_code == 200:
                rate = Decimal(response.json()["rate"])  # Получаем курс и преобразуем в Decimal
            else:
                await message.answer("Произошла ошибка при получении курса валют. Попробуйте позже.")
                return
        except requests.exceptions.RequestException as e:
            await message.answer("Произошла ошибка при получении курса валют. Попробуйте позже.")
            return

    operations = get_operations_by_user(message.chat.id)  # Получаем все операции пользователя из базы данных

    # Вывод информации по каждой операции в выбранной валюте
    for operation in operations:
        operation_date = operation[1].strftime("%d.%m.%Y")  # Преобразование даты операции в строку
        operation_sum = operation[2] / rate if currency != "RUB" else operation[2]  # Пересчет суммы операции в выбранную валюту
        type_operation = operation[4]  # Получаем тип операции
        operation_sum_formatted = "{:.2f}".format(operation_sum)  # Форматирование суммы операции
        await message.answer(f"{operation_date} - {type_operation}: {operation_sum_formatted} {currency}")  # Вывод информации по операции

    await state.clear()  # Очистка состояния после завершения просмотра операций

# Определение состояний для обновления операции
class UpdateOperation(StatesGroup):
    operation_id = State()  # Состояние для идентификатора операции
    new_sum = State()  # Состояние для новой суммы операции

# Обработчик команды на начало обновления операции
@router.message(Command('update_operation'))
async def update_operation_start(message: types.Message, state: FSMContext):
    if not is_user_registered(message.chat.id):  # Проверка, зарегистрирован ли пользователь
        await message.answer("Вы не зарегистрированы. Используйте команду /reg для регистрации.")
        return

    await message.answer("Введите идентификатор операции, которую хотите обновить:")  # Запрос на ввод идентификатора операции
    await state.set_state(UpdateOperation.operation_id)  # Установка состояния на ввод идентификатора операции

# Обработчик сообщения при установленном состоянии operation_id для обновления операции
@router.message(UpdateOperation.operation_id, filters.StateFilter(UpdateOperation.operation_id))
async def operation_id_handler(message: types.Message, state: FSMContext):
    try:
        operation_id = int(message.text)  # Преобразование введенного идентификатора в целое число
    except ValueError:
        await message.answer("Неверный идентификатор операции. Попробуйте еще раз.")
        return

    operations = get_operations_by_user(message.chat.id)  # Получение операций пользователя
    operation_exists = False
    #Переменная operation_exists инициализируется как логическое значение False,
    # что указывает на то, что при начале выполнения цикла ни одна операция из operations пока не была найдена.
    for operation in operations:#цикл for operation in operations: будет перебирать каждую операцию из списка operations
        if operation[0] == operation_id:  # Проверка существования операции с введенным идентификатором
            operation_exists = True
            break

    if not operation_exists:
        await message.answer("Операция с таким идентификатором не существует или не принадлежит вам.")
        return

    await message.answer("Введите новую сумму операции:")  # Запрос на ввод новой суммы операции
    await state.update_data(operation_id=operation_id)  # Обновление данных в состоянии с идентификатором операции
    await state.set_state(UpdateOperation.new_sum)  # Установка состояния на ввод новой суммы операции

# Обработчик сообщения при установленном состоянии new_sum для обновления суммы операции
@router.message(UpdateOperation.new_sum, filters.StateFilter(UpdateOperation.new_sum))
async def new_sum_handler(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Неверная сумма. Попробуйте еще раз.")
        return

    data = await state.get_data()  # Получение данных из состояния
    operation_id = data["operation_id"]  # Получение идентификатора операции из данных
    new_sum = int(message.text)  # Преобразование введенной суммы в целое число
    update_operation(operation_id, new_sum)  # Обновление операции с новой суммой
    await message.answer("Операция успешно обновлена.")  # Уведомление об успешном обновлении операции
    await state.clear()  # Очистка состояния после завершения процесса обновления операции

# Регистрация обработчиков операций
def register_handlers_operations(dp):
    dp.include_router(router)
    #include_router(router) добавляет все обработчики маршрутов (routes) из указанного router в основной механизм обработки сообщений в  боте.
    # Это позволяет объединить все обработчики из router в общую систему обработки сообщений бота.