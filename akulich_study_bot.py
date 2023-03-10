import dataclasses
import enum
import os
from dotenv import load_dotenv
import typing as t
import gspread
from telebot import types, TeleBot
from data_objects import Category, Purchase

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TG_TOKEN')     # подключаемся к боту
bot: TeleBot = TeleBot(TELEGRAM_TOKEN)

# подключаемся к гугл-таблицам
gc = gspread.service_account('/home/daria/PycharmProjects/first_bot/service_account.json')
google_sheet_id = os.getenv('GOOGLE_TOKEN')

users = [463398350, 976045656]


def check_user_id(message):  # проверка юзер ид
    user_id = message.from_user.id
    if user_id not in users:
        return True


@bot.message_handler(func=check_user_id)  # ответ бота, если этому юзер ид нельзя писать
def check_user_permissions(message):
    bot.send_message(message.chat.id, 'Not allowed to talk to strangers')


class StepOfPurchase(enum.Enum):  # шаг, на котором находится юзер
    write_price = 1
    write_comment = 2
    default = 3


@dataclasses.dataclass
class UserState:
    step: StepOfPurchase = StepOfPurchase.default
    purchases: t.Dict[int, Purchase] = dataclasses.field(default_factory=lambda: dict())  # ?
    current_purchase: t.Optional[int] = None  # ?


class Database:
    users: t.Dict[int, UserState] = {}  # состояния. связь id сообщения к состоянию пользователя

    @staticmethod
    def get_state(user_id: int) -> UserState:  # ?
        return Database.users.get(user_id)


class Configuration:  # заменяем calldadta кнопок
    ADD_CATEGORY_KEY = 'add_category'
    ADD_PRICE_KEY = 'add_price'
    ADD_COMMENT_KEY = 'add_comment'
    DONE_PURCHASE_KEY = 'done_purchase'


class ConfigTexts:  # вместо текста на кнопках
    NEW_PURCHASE = 'New purchase'
    ADD_CATEGORY = 'Add category'
    ADD_PRICE = 'Add price'
    ADD_COMMENT = 'Add comment'
    FINISH_PURCHASE = 'Finish purchase'


@bot.message_handler(commands=['start'])  # Начало чата и начало новой покупки
def start(message):
    start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton(ConfigTexts.NEW_PURCHASE)
    start_markup.add(button1)
    bot.send_message(message.chat.id, text="Ready to make a purchase?", reply_markup=start_markup)


# Основная клав-ра, с которой будет происходить добавление покупок
def create_inline_kb(purchase: t.Optional[Purchase] = None) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton(text=ConfigTexts.ADD_CATEGORY, callback_data=Configuration.ADD_CATEGORY_KEY)
    button2 = types.InlineKeyboardButton(text=ConfigTexts.ADD_PRICE, callback_data=Configuration.ADD_PRICE_KEY)
    button3 = types.InlineKeyboardButton(text=ConfigTexts.ADD_COMMENT, callback_data=Configuration.ADD_COMMENT_KEY)
    button4 = types.InlineKeyboardButton(text=ConfigTexts.FINISH_PURCHASE,
                                         callback_data=Configuration.DONE_PURCHASE_KEY)

    if purchase is not None:
        if purchase.category is not None:
            button1 = types.InlineKeyboardButton(text=purchase.category, callback_data=Configuration.ADD_CATEGORY_KEY)
        if purchase.price is not None:
            button2 = types.InlineKeyboardButton(text=purchase.price, callback_data=Configuration.ADD_PRICE_KEY)
        if purchase.name is not None:
            button3 = types.InlineKeyboardButton(text=purchase.name, callback_data=Configuration.ADD_COMMENT_KEY)

    markup.add(button1, button2, button3, button4)
    return markup


# декоратор, который реагирует на сообщение "Новая покупка", с которого начинается добавление этой новой покупки
@bot.message_handler(content_types=['text'], regexp=f'^{ConfigTexts.NEW_PURCHASE}$')
def get_text_messages(message):
    # выводится клав-ра
    message = bot.send_message(message.chat.id, 'Enter purchase details:', reply_markup=create_inline_kb())
    # получаем ид юзера из дата базы
    user = Database.users.get(message.chat.id)
    if user is None:
        user = Database.users[message.chat.id] = UserState()    # ?

    user.purchases[message.id] = Purchase(is_closed=False)  # Добавляем в покупку этот юзер ид


@bot.callback_query_handler(func=lambda call: call.data == Configuration.ADD_CATEGORY_KEY)  # done
def choose_category(call):
    category_markup = types.InlineKeyboardMarkup(row_width=2)
    temp_array = []
    for category in Category:
        bbt = types.InlineKeyboardButton(f'{category.name}', callback_data=category.name)
        temp_array.append(bbt)
        if len(temp_array) == 2:
            category_markup.row(temp_array[0], temp_array[1])
            temp_array = []
    if len(temp_array) == 1:
        category_markup.row(temp_array[0])

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=category_markup,
        text='Choose category:'
    )


@bot.callback_query_handler(func=lambda call: call.data in Category.__members__)
def add_category(call):
    user = Database.users.get(call.message.chat.id)
    purchase = user.purchases.get(call.message.id)
    if purchase is not None:
        purchase.category = Category[call.data].name

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text="The category has been entered. What's next?", reply_markup=create_inline_kb(purchase))


@bot.callback_query_handler(func=lambda call: call.data == Configuration.ADD_PRICE_KEY)
def enter_price(call):
    bot.send_message(call.message.chat.id, 'Enter price:')
    user = Database.users.get(call.message.chat.id)
    if user is not None:
        user.step = StepOfPurchase.write_price
        user.current_purchase = call.message.id
    else:
        bot.send_message(call.message.chat.id, 'Sry purchase is not active')


@bot.message_handler(
    content_types=['text'],
    func=lambda message: Database.users.get(message.chat.id).step is StepOfPurchase.write_price)
def add_price(message):
    user = Database.users.get(message.chat.id)
    purchase = user.purchases.get(user.current_purchase)
    if purchase is not None:
        purchase.price = message.text

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=user.current_purchase,
        text="The price has been entered. What's next?", reply_markup=create_inline_kb(purchase))

    user.step = StepOfPurchase.default


@bot.callback_query_handler(func=lambda call: call.data == Configuration.ADD_COMMENT_KEY)
def enter_comment(call):
    bot.send_message(call.message.chat.id, 'Enter comment:')
    user = Database.users.get(call.message.chat.id)
    if user is not None:
        user.step = StepOfPurchase.write_comment
        user.current_purchase = call.message.id
    else:
        bot.send_message(call.message.chat.id, 'Sry purchase is not active')


@bot.message_handler(
    content_types=['text'],
    func=lambda message: Database.users.get(message.chat.id).step is StepOfPurchase.write_comment)
def add_comment(message):
    user = Database.users.get(message.chat.id)
    purchase = user.purchases.get(user.current_purchase)
    if purchase is not None:
        purchase.name = message.text

    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=user.current_purchase,
        text="The comment has been entered. What's next?", reply_markup=create_inline_kb(purchase))

    user.step = StepOfPurchase.default


@bot.callback_query_handler(func=lambda call: call.data == Configuration.DONE_PURCHASE_KEY)
def result(call):
    bot.send_message(call.message.chat.id, "It's all set")
    user = Database.users.get(call.message.chat.id)
    purchase = user.purchases.get(call.message.id)
    if purchase is not None:
        purchase.is_closed = True

    sh = gc.open_by_key(google_sheet_id)
    sh.sheet1.append_row([purchase.category, purchase.price, purchase.name])


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    bot.send_message(message.chat.id, 'what are these numbers? go to hell')


if __name__ == '__main__':
    print('started')
    bot.polling(none_stop=True, interval=0)
    print('stoped')
