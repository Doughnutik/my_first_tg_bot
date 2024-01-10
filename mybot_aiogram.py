from aiogram import Bot, Dispatcher, types, executor
from aiogram.types.web_app_info import WebAppInfo
import config

bot = Bot(config.BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton('Открыть гитхаб бота', web_app=WebAppInfo(url='https://github.com/Doughnutik/my_first_tg_bot')))
    markup.add(types.KeyboardButton('Открыть мой сайт', web_app=WebAppInfo(url='https://index.html')))
    await message.answer('Привет', reply_markup=markup) 
    
executor.start_polling(dp)