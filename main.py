import asyncio
import random
import requests
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import TOKEN, API_KEY

bot = Bot(token=TOKEN)
dp = Dispatcher()
api_key = API_KEY

# Список команд и их описаний
commands = [
    BotCommand(command="start", description="Запустить бота"),
    BotCommand(command="help", description="Помощь"),
    BotCommand(command="weather", description="Узнать погоду"),
    BotCommand(command="photo", description="Получить фото Бендера"),
]

async def on_startup(bot: Bot):
    await set_main_menu(bot)


async def set_main_menu(bot: Bot):
    await bot.set_my_commands(commands=commands)

class WeatherState(StatesGroup):
    waiting_for_city = State()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer('Привет!')


@dp.message(Command('help'))
async def help(message: Message):
    await message.answer('Этот бот умеет выполнять команды:\n/help - вывести помощь\n/start - начать работу')

@dp.message(Command('photo'))
async def photo(message: Message):
    list = [
        'https://i.pinimg.com/736x/da/ad/01/daad012cd2fcbc11471425a44b282ca1.jpg',
        'https://yt3.googleusercontent.com/ytc/AIdro_n9UZElISPn9dNQ2MVwngMkUBTsBJBjO16IXrqcGWFMqA=s900-c-k-c0x00ffffff-no-rj',
        'https://habrastorage.org/r/w1560/getpro/habr/upload_files/ea8/ae6/1fd/ea8ae61fd4b2867f6c7e2137a4aaf200.png',
    ]
    await message.answer_photo(photo=random.choice(list), caption='Бендер топ')

# Обработчик команды /weather
@dp.message(Command('weather'))
async def cmd_weather(message:Message, state: FSMContext):
    await message.answer("Введите название города:")
    await state.set_state(WeatherState.waiting_for_city)

# Обработчик города (только в состоянии waiting_for_city)
@dp.message(WeatherState.waiting_for_city)
async def process_city(message:Message, state: FSMContext):
    city = message.text
    weather_info = await get_weather(city)
    await message.answer(weather_info)
    await state.clear()  # сбрасываем состояние

@dp.message(F.text == 'Привет')
async def echo(message: Message):
    await message.answer('Привет! Я бот!')

@dp.message(F.photo)
async def react_photo(message: Message):
    list = [
        'Огонь',
        'Непонятное',
        'Не отправляй мне такое',
    ]
    await message.answer(random.choice(list))

async def get_weather(city):
    try:
        response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric')
        data = response.json()
        temp = data['main']['temp']
        pressure = data['main']['pressure']
        humidity = data['main']['humidity']
        return f'В городе {city} сейчас {temp} градусов, давление {round(pressure * 0.750062)} мм рт ст, влажность {humidity}%'
    except Exception as ex:
        return 'Проверьте название города'

async def main():
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())