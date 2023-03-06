import os

import telebot
from telebot import types, TeleBot
import sqlite3
import gspread
from datetime import date

dic = {'category': '', 'price': '', 'comment': ''}
TOKEN = ''
bot: TeleBot = telebot.TeleBot(TOKEN)
gc = gspread.service_account("/home/daria/PycharmProjects/first_bot/service_account.json")
google_sheet_id = os.getenv('TOKEN')
categories = [
    'cafe', 'food'
]


def sqlite_connect():
    conn = sqlite3.connect('/home/daria/PycharmProjects/first_bot/identifier.sqlite', check_same_thread=False)
    return conn


def check_user_id(message):
    user_id = message.from_user.id
    conn = sqlite_connect()
    c = conn.cursor()
    info = c.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    return info.fetchone() is None


@bot.message_handler(func=check_user_id)
def check(message):
    bot.send_message(message.chat.id, 'Не дозволено общаться с незнакомцами')
    print(message.from_user.id)


@bot.message_handler(commands=['start'])
def start(message):
    start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Новая покупка')
    start_markup.add(button1)
    bot.send_message(message.chat.id, text="Готов внести покупку?".format(message.from_user), reply_markup=start_markup)


# декоратор, который реагирует на входящие сообщения и содержит в себе функцию ответа
@bot.message_handler(content_types=['text'])  # метод для получения текстовых сообщений
def get_text_messages(message):
    if message.text == "Новая покупка":
        markup = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton('Внести категорию', callback_data='category')
        button2 = types.InlineKeyboardButton('Внести цену', callback_data='price')
        button3 = types.InlineKeyboardButton('Внести комментарий', callback_data='comment')
        button4 = types.InlineKeyboardButton('Подтвердить покупку', callback_data='done')
        markup.add(button1, button2, button3, button4)
        bot.send_message(message.chat.id, 'Что мне сделать?', reply_markup=markup)

    # elif (message.text == "Добавить категорию"):
    #     category = message.text
    #
    # elif (message.text == 'Добавить цену'):
    #     price = message.text
    #
    # elif (message.text == 'Добавить комментарий'):
    #     comment = message.text
    #
    # elif (message.text == 'Подтвердить покупку'):
    #     text_message = 'Entry added'
    #     bot.send_message(message.from_user.id, text_message)
    #
    #     today_date = date.today().strftime("%d.%m.%Y")
    #     sh = gc.open_by_key(google_sheet_id)
    #     sh.sheet1.append_row([message.from_user.id, today_date, category, price])

        # bot.send_message(message.chat.id, "У меня нет имени..")

        # category, price = message.text.split("-", 1)


@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    if call.message:
        if call.data == 'choose_category':
            # bot.send_message(call.message.chat.id, f'Введите категорию:')
            markup = types.InlineKeyboardMarkup(row_width=1)
            button1 = types.InlineKeyboardButton('Внести категорию', callback_data='category')
            button2 = types.InlineKeyboardButton('Внести цену', callback_data='price')
            button3 = types.InlineKeyboardButton('Внести комментарий', callback_data='comment')
            button4 = types.InlineKeyboardButton('Подтвердить покупку', callback_data='done')
            markup.add(button1, button2, button3, button4)
            # dic['category'] = call.message
            # print(dic['category'])
            bot.edit_message_reply_markup()
            bot.send_message(call.message.chat.id, f'Категория {dic["category"]}:')
        if call.data == 'category':
            pass




if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
