import telebot
from src.config import Configuration, gc
from src.data_objects import UserState, Category, Purchase, StepOfPurchase
from src.database import Database
from src.keyboard_factory import create_inline_kb, choose_category_kb
from telebot.types import Message, CallbackQuery
from src.middleware import check_user_id, check_purchase_middleware
from telebot import types


def init(bot: telebot.TeleBot, db: Database):
    @bot.message_handler(
        content_types=['text'],
        func=lambda message: (user := db.get_user(message.chat.id)) is not None
        and user.step is StepOfPurchase.write_price)
    @check_purchase_middleware(db)
    def add_price(message: Message, user: UserState, purchase: Purchase):
        purchase.price = message.text
        user.step = StepOfPurchase.default

        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user.current_purchase,
            text="The price has been entered. What's next?", reply_markup=create_inline_kb(purchase))

    @bot.callback_query_handler(func=lambda call: call.data == Configuration.ADD_COMMENT_KEY)
    @check_purchase_middleware(db)
    def enter_comment(call: CallbackQuery, user: UserState, _):
        bot.send_message(call.message.chat.id, 'Enter comment:')
        user.step = StepOfPurchase.write_comment
        user.current_purchase = call.message.id

    @bot.message_handler(
        content_types=['text'],
        func=lambda message: (user := db.get_user(message.chat.id)) is not
        None and user.step is StepOfPurchase.write_comment
    )
    @check_purchase_middleware(db)
    def add_comment(message: Message, user: UserState, purchase: Purchase):
        purchase.name = message.text
        user.step = StepOfPurchase.default

        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=user.current_purchase,
            text="The comment has been entered. What's next?", reply_markup=create_inline_kb(purchase))

    @bot.callback_query_handler(func=lambda call: call.data == Configuration.DONE_PURCHASE_KEY)
    @check_purchase_middleware(db)
    def result(call: CallbackQuery, _: UserState, purchase: Purchase):
        purchase.is_closed = True
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            reply_markup=None,
            text=f'Purchase {purchase.name} \nCategory {purchase.category.value}\nPrice {purchase.price} RSD\ndone')
        sh = gc.open_by_key(Configuration.GOOGLE_TOKEN)
        sh.sheet1.append_row([purchase.category.value, purchase.price, purchase.name])

    @bot.message_handler(func=check_user_id)  # ответ бота, если этому юзер ид нельзя писать
    def check_user_permissions(message):
        bot.send_message(message.chat.id, 'Not allowed to talk to strangers')

    @bot.message_handler(commands=['start'])  # Начало чата и начало новой покупки
    def start(message: Message):
        start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton(Configuration.NEW_PURCHASE)
        start_markup.add(button1)
        bot.send_message(message.chat.id, text="Ready to make a purchase?", reply_markup=start_markup)

    @bot.message_handler(content_types=['text'], regexp=f'^{Configuration.NEW_PURCHASE}$')
    def get_text_messages(message: Message):
        # выводится клав-ра
        message = bot.send_message(message.chat.id, 'Enter purchase details:', reply_markup=create_inline_kb())
        # получаем ид юзера из дата базы
        user = db.get_user(message.chat.id)
        if user is None:
            user = db.create_user(message.chat.id)

        user.purchases[message.id] = Purchase(is_closed=False)  # Добавляем в покупку этот юзер ид

    @bot.callback_query_handler(func=lambda call: call.data == Configuration.ADD_CATEGORY_KEY)  # done
    def choose_category(call: CallbackQuery):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            reply_markup=choose_category_kb(),
            text='Choose category:'
        )

    @bot.callback_query_handler(func=lambda call: call.data in Category.__members__)
    @check_purchase_middleware(db)
    def add_category(call: CallbackQuery, _: UserState, purchase: Purchase):
        purchase.category = Category[call.data]
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text="The category has been entered. What's next?", reply_markup=create_inline_kb(purchase))

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message: Message):
        bot.send_message(message.chat.id, 'what are these numbers? I dont understand')

    @bot.callback_query_handler(func=lambda call: call.data == Configuration.ADD_PRICE_KEY)
    @check_purchase_middleware(db)
    def enter_price(call: CallbackQuery, user: UserState, _: Purchase):
        user.step = StepOfPurchase.write_price
        user.current_purchase = call.message.id

        bot.send_message(call.message.chat.id, 'Enter price:')
