import telebot
import webbrowser
from telebot import types
import sqlite3
import config
import requests
import json

import os.path as op
import urllib.request
from datetime import date
from currency_converter import ECB_URL, CurrencyConverter
from currency_converter import currency_converter

filename = f"ecb_{date.today():%Y%m%d}.zip"
if not op.isfile(filename):
    urllib.request.urlretrieve(ECB_URL, filename)
currency = CurrencyConverter(filename)

bot = telebot.TeleBot(config.BOT_TOKEN)

@bot.message_handler(commands=['weather'])
def get_weather(message):
    bot.reply_to(message, 'Укажите город, в котором вас интересует погода')
    bot.register_next_step_handler(message, get_city_weather)

def get_city_weather(message):
    city = message.text.strip().lower()
    result = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={config.API_WEATHER}&units=metric&lang=ru')
    if result.status_code == 200:
        data = json.loads(result.text)
        print(data)
        bot.reply_to(message, f'''Погода в {city}:
Температура: {data['main']['temp']} 
Ощущается: {data['main']['feels_like']}
Осадки: {data['weather'][0]['description']}
Давление: {0.75 * int(data['main']['pressure'])} мм рт. ст.
Видимость: {data['visibility']} метров
Скорость ветра: {data['wind']['speed']} м/c
Направление ветра: {data['wind']['deg']} градусов
        ''')
    else:
        bot.reply_to(message, 'Ошибка запроса')
        
@bot.message_handler(content_types=['voice'])
def get_audio(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Перейти к генералу Перепечко', url='https://vuzopedia.ru/storage/app/uploads/public/646/729/192/6467291920247857574894.jpg')
    btn2 = types.InlineKeyboardButton('Удалить высказывание', callback_data='delete')
    btn3 = types.InlineKeyboardButton('Изменить высказывание', callback_data='edit')
    markup.row(btn1, btn2)
    markup.add(btn3)
    bot.reply_to(message, 'Кто тебе позволил говорить, салага?', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data == 'edit' or callback.data == 'delete')
def callback_message(callback):
    if callback.data == 'delete':
        bot.delete_message(callback.message.chat.id, callback.message.message_id - 1)
        bot.edit_message_text('Слово не воробей, но генерал его поймал', callback.message.chat.id, callback.message.message_id)
    elif callback.data == 'edit':
        bot.edit_message_text('Генерал Перепечко прибыл на задание', callback.message.chat.id, callback.message.message_id)

@bot.message_handler(commands=['site'])
def site(message):
    bot.send_message(message.chat.id, 'Введите нужный вам сайт (можно без https)')
    bot.register_next_step_handler(message, open_site)
    
def open_site(message):
    text = message.text.strip()
    if len(text) < 8 or text[:8] != 'https://':
        webbrowser.open('https://' + text)
    else:
        webbrowser.open(text)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Приветствую тебя, солдат {message.from_user.first_name} {message.from_user.last_name}. На связи генерал Перепечко!')
    file = open('sticker.webm', 'rb')
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAJqJmWFSLn_grAMe0BdjQNCfJlr6k3ZAAIOFQACRAE5SsHbSRQzXgWqMwQ')
    file = open('video.mp4', 'rb')
    bot.send_video(message.chat.id, file)

@bot.message_handler(commands=['register'])
def register(message):
    conn = sqlite3.connect('mybot.db')
    cur = conn.cursor()
    
    cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto increment primary key, name varchar(50), password varchar(50))')
    conn.commit()
    cur.close()
    conn.close()
    
    bot.send_message(message.chat.id, 'Введи имя для регистрации')
    bot.register_next_step_handler(message, add_name_to_db)
    
def add_name_to_db(message):
    name = message.text.strip()
    
    if name.lower() == 'perepechko' or name.lower() == 'перепечко':
        bot.reply_to(message, 'Генерал всегда зарегистрирован. Вводи другое имя')
        bot.register_next_step_handler(message, add_name_to_db)
        return
    conn = sqlite3.connect('mybot.db')
    cur = conn.cursor()
    cur.execute("SELECT rowid FROM users WHERE name = ?", (name,))
    data = cur.fetchone()
    if data:
        bot.reply_to(message, 'Данный пользователь уже существует')
        cur.close()
        conn.close()
        return
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Введи пароль для регистрации')
    bot.register_next_step_handler(message, add_password_to_db, name)
    
    
def add_password_to_db(message, name):
    password = message.text.strip()
    conn = sqlite3.connect('mybot.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, password) VALUES ('%s', '%s')" % (name, password))
    conn.commit()
    cur.close()
    conn.close()
    
    bot.send_message(message.chat.id, 'Успешно зарегистрирован')
    
@bot.message_handler(commands=['delete'])
def delete(message):
    bot.send_message(message.chat.id, 'Введи пользователя, которого хотите удалить')
    bot.register_next_step_handler(message, delete_name_from_db)
    
def delete_name_from_db(message):
    name = message.text.strip()
    conn = sqlite3.connect('mybot.db')
    cur = conn.cursor()
    cur.execute("SELECT rowid FROM users WHERE name = ?", (name,))
    data = cur.fetchone()
    if not data:
        bot.reply_to(message, 'Данного пользователя не существует')
        cur.close()
        conn.close()
        return
    cur.execute("DELETE FROM users WHERE name = ?", (name,))
    conn.commit()
    cur.close()
    conn.close()
    bot.reply_to(message, "Пользователь успешно удалён")
    
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'С какой стати генерал должен помогать какому-то солдатишке? И вообще, почему тебе кто-то должен помогать. Генерал Перепечко добивался всего сам, кровью и потом!!! Ты ни от кого не должен зависеть, ты взрослый бугай, огромный лоб с мозгами, так что быстро взял себя в руки, зарядился мотивацией и пошёл покорять этот мир!')
    
@bot.message_handler(commands=['users'])
def users(message):
    conn = sqlite3.connect('mybot.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    
    info = ''
    for user in users:
        info += f'Имя: {user[1]}, Пароль: {user[2]}\n'
    
    cur.close()
    conn.close()
    
    bot.send_message(message.chat.id, info)

@bot.message_handler(commands=['convert'])
def convert(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    usd_eur_btn = types.InlineKeyboardButton('USD/EUR', callback_data='conv/USD/EUR')
    eur_usd_btn = types.InlineKeyboardButton('EUR/USD', callback_data='conv/EUR/USD')
    rub_cny_btn = types.InlineKeyboardButton('RUB/CNY', callback_data='conv/RUB/CNY')
    cny_rub_btn = types.InlineKeyboardButton('CNY/RUB', callback_data='conv/CNY/RUB')
    rub_usd_btn = types.InlineKeyboardButton('RUB/USD', callback_data='conv/RUB/USD')
    rub_eur_btn = types.InlineKeyboardButton('RUB/EUR', callback_data='conv/RUB/EUR')
    usd_rub_btn = types.InlineKeyboardButton('USD/RUB', callback_data='conv/USD/RUB')
    eur_rub_btn = types.InlineKeyboardButton('EUR/RUB', callback_data='conv/EUR/RUB')
    other_btn = types.InlineKeyboardButton('Другая пара валют', callback_data='conv/other')
    markup.add(usd_eur_btn, eur_usd_btn, rub_cny_btn, cny_rub_btn, rub_usd_btn, usd_rub_btn, rub_eur_btn, eur_rub_btn, other_btn)
    bot.send_message(message.chat.id, 'Выбери пару валют', reply_markup=markup)
    
@bot.callback_query_handler(func=lambda call: call.data.startswith('conv'))
def callback(call):
    if call.data == 'conv/other':
        bot.send_message(call.message.chat.id, 'Введи нужную пару валют через / (как было указано выше)')
        bot.register_next_step_handler(call.message, get_pair_of_values)
    else:
        get_pair_of_values(call.message, call.data.split('/')[1:])
    
def get_pair_of_values(message, values=None):
    if not values:
        values = message.text.upper().split('/')
        if len(values) != 2:
            bot.reply_to(message, 'Неверный формат')
            bot.register_next_step_handler(message, get_pair_of_values)
            return
    bot.send_message(message.chat.id, 'Введите сумму для конвертации')
    bot.register_next_step_handler(message, get_sum, values)
    
def get_sum(message, values):
    text = message.text.strip()
    if not text.isdigit():
        bot.reply_to(message, 'Некорректное значение, солдат. Чему тебя в школе вообще учили? Вводи ещё раз!')
        bot.register_next_step_handler(message, get_sum)
        return
    sum = int(text)
    if sum <= 0:
        bot.reply_to(message, 'Я конечно не математик, но про натуральные числа слышал')
        bot.register_next_step_handler(message, get_sum)
        return
    bot.send_message(message.chat.id, 'Укажите интересующую вас дату в формате ГГГГ, ММ, ДД. Если хочется конвертировать по текущему курсу, напишите today')
    bot.register_next_step_handler(message, get_date, values, sum)
    
def get_date(message, values, sum):
    text = message.text
    need_date = f'{date.today():%Y%m%d}'
    print(need_date)
    if text.lower() != 'today':
        need_date = date(text)
    try:
        res = currency.convert(sum, values[0], values[1], date=date(need_date))
    except ValueError:
        bot.send_message(message.chat.id, 'Генерал с похмелья не может выполнить данную операцию')
    except currency_converter.RateNotFoundError:
        last1 = currency.bounds[values[0]][1]
        last2 = currency.bounds[values[1]][2]
        
    else:
        bot.send_message(message.chat.id, f'Результат обнала: {res}')
    
@bot.message_handler()
def info(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, f'{message.from_user.first_name} {message.from_user.last_name}, не привет, а здравия желаю!')
    elif message.text.lower() == 'здравия желаю':
        bot.send_message(message.chat.id, f'Так точно, {message.from_user.first_name} {message.from_user.last_name}. Да начнётся АРМИЯ!')
    elif message.text.lower() == 'id':
        bot.reply_to(message, message.from_user.id)
    else:
        bot.send_message(message.chat.id, 'Сильное заявление, проверять я его, конечно, не буду')

bot.infinity_polling()