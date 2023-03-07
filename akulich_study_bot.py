import dataclasses
import enum
import os
import sqlite3
from dataclasses import field

import gspread
import telebot
from dotenv import load_dotenv
from telebot import types, TeleBot

from data_objects import Purchase

load_dotenv()
import typing as t


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot: TeleBot = telebot.TeleBot(TELEGRAM_TOKEN)

gc = gspread.service_account("service_account.json")
google_sheet_id = os.getenv('GOOGLE_ID_TOKEN')
categories = [
    'cafe', 'food'
]


class StepOfPurchase(enum.Enum):
    write_price = 1
    write_comment = 2
    default = 3


@dataclasses.dataclass
class UserState:
    step: StepOfPurchase = StepOfPurchase.default
    purchases: t.Dict[int, Purchase] = field(default_factory=lambda: dict())
    current_purchase: t.Optional[int] = None


class Database:
    users: t.Dict[int, UserState] = {}  # состояния. связь сообщения к покупке

    @staticmethod
    def get_state(user_id: int) -> UserState:
        return Database.users.get(user_id)


class Configuration:
    ADD_CATEGORY_KEY = 'add_category'
    ADD_PRICE_KEY = 'add_price'
    ADD_COMMENT_KEY = 'add_comment'
    DONE_PURCHASE_KEY = 'done_purchase'


class ConfigTexts:
    NEW_PURCHASE = 'Новая покупка'


def check_user_id(message):
    user_id = message.from_user.id
    with sqlite3.connect('identifier.sqlite', check_same_thread=False) as conn:
        c = conn.cursor()
        info = c.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    return info.fetchone() is None


@bot.message_handler(func=check_user_id)
def check_user_permissions(message):
    bot.send_message(message.chat.id, 'Не дозволено общаться с незнакомцами')


@bot.message_handler(commands=['start'])
def start(message):
    start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton(ConfigTexts.NEW_PURCHASE)
    start_markup.add(button1)
    bot.send_message(message.chat.id, text="Готов внести покупку?".format(message.from_user), reply_markup=start_markup)


def create_inline_kb() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton('Внести категорию', callback_data=Configuration.ADD_CATEGORY_KEY)
    button2 = types.InlineKeyboardButton('Внести цену', callback_data=Configuration.ADD_PRICE_KEY)
    button3 = types.InlineKeyboardButton('Внести комментарий', callback_data=Configuration.ADD_COMMENT_KEY)
    button4 = types.InlineKeyboardButton('Подтвердить покупку', callback_data=Configuration.DONE_PURCHASE_KEY)
    markup.add(button1, button2, button3, button4)
    return markup


# декоратор, который реагирует на входящие сообщения и содержит в себе функцию ответа
@bot.message_handler(content_types=['text'], regexp=f'^{ConfigTexts.NEW_PURCHASE}$')  # метод для получения текстовых сообщений
def get_text_messages(message):
    message = bot.send_message(message.chat.id, 'Введите детали покупки', reply_markup=create_inline_kb())
    user = Database.users.get(message.chat.id)
    if user is None:
        user = Database.users[message.chat.id] = UserState()

    user.purchases[message.id] = Purchase(is_closed=False)


@bot.callback_query_handler(func=lambda call: call.data == Configuration.ADD_CATEGORY_KEY)
def handle(call):
    bot.send_message(call.message.chat.id, 'huj')


@bot.callback_query_handler(func=lambda call: call.data == Configuration.ADD_PRICE_KEY)
def handle(call):
    user = Database.users.get(call.message.chat.id)
    user.current_purchase = call.message.id
    user.step = StepOfPurchase.write_price

    bot.send_message(call.message.chat.id, 'Введи цену')


@bot.message_handler(
    content_types=['text'],
    func=lambda message: Database.users.get(message.chat.id).step is StepOfPurchase.write_price)
def get_text_messages(message):
    user = Database.users.get(message.chat.id)
    user.purchases[user.current_purchase].price = int(message.text)
    user.step = StepOfPurchase.default


@bot.callback_query_handler(func=lambda call: call.data == Configuration.ADD_COMMENT_KEY)
def handle(call):
    bot.send_message(call.message.chat.id, 'huj')

    # if call.message:
    #     if call.data == 'choose_category':
    #         # bot.send_message(call.message.chat.id, f'Введите категорию:')
    #         markup = types.InlineKeyboardMarkup(row_width=1)
    #         button1 = types.InlineKeyboardButton('Внести категорию', callback_data='category')
    #         button2 = types.InlineKeyboardButton('Внести цену', callback_data='price')
    #         button3 = types.InlineKeyboardButton('Внести комментарий', callback_data='comment')
    #         button4 = types.InlineKeyboardButton('Подтвердить покупку', callback_data='done')
    #         markup.add(button1, button2, button3, button4)
    #         # dic['category'] = call.message
    #         # print(dic['category'])
    #         bot.edit_message_reply_markup()
    #         bot.send_message(call.message.chat.id, f'Категория {dic["category"]}:')
    #     if call.data == 'category':
    #         pass



# def check_purchase_in_memory_for_callback(func):
#     def wrapper(call):
#         if Database.purchases.get(call.message.id) is None:
#             bot.send_message(call.message.chat.id)
#         return func(call)
#     return wrapper


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    bot.send_message(message.chat.id, 'че это за цифры? иди на хуй')


if __name__ == '__main__':
    print('started')
    bot.polling(none_stop=True, interval=0)
    print('stoped')
