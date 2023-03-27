import typing as t
from src.config import Configuration, gc
from src.data_objects import UserState, Category, Purchase, StepOfPurchase
from src.keyboard_factory import create_inline_kb, choose_category_kb
from telebot import types
from src.pydantic_models import TelegramUpdate, CallbackUpdate, MessageUpdate


# def init(bot: telebot.TeleBot, db: Database):
#     @bot.message_handler(
#         content_types=['text'],
#         func=lambda message: db.get_user(message.chat.id) is not None
#                              and db.get_user(message.chat.id).step is StepOfPurchase.write_price)
#     @check_purchase_middleware(db)
#     def add_price(message: Message, user: UserState, purchase: Purchase):
#         purchase.price = message.text
#         user.step = StepOfPurchase.default
#
#         bot.edit_message_text(
#             chat_id=message.chat.id,
#             message_id=user.current_purchase,
#             text="The price has been entered. What's next?", reply_markup=create_inline_kb(purchase))
#
#     @bot.callback_query_handler(func=lambda call: call.data == Configuration.ADD_COMMENT_KEY)
#     @check_purchase_middleware(db)
#     def enter_comment(call: CallbackQuery, user: UserState, _):
#         bot.send_message(call.message.chat.id, 'Enter comment:')
#         user.step = StepOfPurchase.write_comment
#         user.current_purchase = call.message.id
#
#     @bot.message_handler(
#         content_types=['text'],
#         func=lambda message: db.get_user(message.chat.id) is not
#                              None and db.get_user(message.chat.id).step is StepOfPurchase.write_comment
#     )
#     @check_purchase_middleware(db)
#     def add_comment(message: Message, user: UserState, purchase: Purchase):
#         purchase.name = message.text
#         user.step = StepOfPurchase.default
#
#         bot.edit_message_text(
#             chat_id=message.chat.id,
#             message_id=user.current_purchase,
#             text="The comment has been entered. What's next?", reply_markup=create_inline_kb(purchase))
#
#     @bot.callback_query_handler(func=lambda call: call.data == Configuration.DONE_PURCHASE_KEY)
#     @check_purchase_middleware(db)
#     def result(call: CallbackQuery, _: UserState, purchase: Purchase):
#         purchase.is_closed = True
#         bot.edit_message_text(
#             chat_id=call.message.chat.id,
#             message_id=call.message.id,
#             reply_markup=None,
#             text=f'Purchase {purchase.name} \nCategory {purchase.category.value}\nPrice {purchase.price} RSD\ndone')
#         sh = gc.open_by_key(Configuration.GOOGLE_TOKEN)
#         sh.sheet1.append_row([purchase.category.value, purchase.price, purchase.name])
#
#     @bot.message_handler(func=check_user_id)  # ответ бота, если этому юзер ид нельзя писать
#     def check_user_permissions(message):
#         bot.send_message(message.chat.id, 'Not allowed to talk to strangers')
#
#     @bot.message_handler(commands=['start'])  # Начало чата и начало новой покупки
#     def start(message: Message):
#         start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         button1 = types.KeyboardButton(Configuration.NEW_PURCHASE)
#         start_markup.add(button1)
#         bot.send_message(message.chat.id, text="Ready to make a purchase?", reply_markup=start_markup)
#
#     @bot.message_handler(content_types=['text'], regexp=f'^{Configuration.NEW_PURCHASE}$')
#     def get_text_messages(message: Message):
#         # выводится клав-ра
#         message = bot.send_message(message.chat.id, 'Enter purchase details:', reply_markup=create_inline_kb())
#         # получаем ид юзера из дата базы
#         user = db.get_user(message.chat.id)
#         if user is None:
#             user = db.create_user(message.chat.id)
#
#         user.purchases[message.id] = Purchase(is_closed=False)  # Добавляем в покупку этот юзер ид
#
#     @bot.callback_query_handler(func=lambda call: call.data == Configuration.ADD_CATEGORY_KEY)  # done
#     def choose_category(call: CallbackQuery):
#         bot.edit_message_text(
#             chat_id=call.message.chat.id,
#             message_id=call.message.id,
#             reply_markup=choose_category_kb(),
#             text='Choose category:'
#         )
#
#     @bot.callback_query_handler(func=lambda call: call.data in Category.__members__)
#     @check_purchase_middleware(db)
#     def add_category(call: CallbackQuery, _: UserState, purchase: Purchase):
#         purchase.category = Category[call.data]
#         bot.edit_message_text(
#             chat_id=call.message.chat.id,
#             message_id=call.message.id,
#             text="The category has been entered. What's next?", reply_markup=create_inline_kb(purchase))
#
#     @bot.message_handler(content_types=['text'])
#     def get_text_messages(message: Message):
#         bot.send_message(message.chat.id, 'what are these numbers? I dont understand')
#
#     @bot.callback_query_handler(func=lambda call: call.data == Configuration.ADD_PRICE_KEY)
#     @check_purchase_middleware(db)
#     def enter_price(call: CallbackQuery, user: UserState, _: Purchase):
#         user.step = StepOfPurchase.write_price
#         user.current_purchase = call.message.id
#
#         bot.send_message(call.message.chat.id, 'Enter price:')


class MessageProcessor:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    def process(self, telegram_update: TelegramUpdate):
        if isinstance(telegram_update, CallbackUpdate):
            self.process_callback(telegram_update)
        elif isinstance(telegram_update, MessageUpdate):
            self.process_message(telegram_update)

    def check_user_id(self, request: MessageUpdate) -> bool:
        user_id = request.message.chat.id
        if user_id in Configuration.USERS:
            return True
        return False

    def process_callback(self, callback: CallbackUpdate):
        user, purchase = self.get_user_and_purchase(callback)

        if callback.callback_query.data == Configuration.ADD_PRICE_KEY:
            self.enter_price(callback, user, purchase)
        if callback.callback_query.data == Configuration.ADD_CATEGORY_KEY:
            self.choose_category(callback)
        if callback.callback_query.data == Configuration.DONE_PURCHASE_KEY:
            self.result(callback, user, purchase)
        if callback.callback_query.data == Configuration.ADD_COMMENT_KEY:
            self.enter_comment(callback, user, purchase)
        if callback.callback_query.data in Category.__members__:
            self.add_category(callback, user, purchase)

    def get_user_and_purchase(self, telegram_update: TelegramUpdate) -> t.Tuple[UserState, Purchase]:
        if isinstance(telegram_update, MessageUpdate):
            chat_id = telegram_update.message.chat.id
            user = self.db.get_user(chat_id)
            message_id = user.current_purchase
        elif isinstance(telegram_update, CallbackUpdate):
            chat_id = telegram_update.callback_query.message.chat.id
            user = self.db.get_user(chat_id)
            message_id = telegram_update.callback_query.message.message_id
        else:
            raise ValueError('Invalid object')

        if user is None:
            raise ValueError('user is None')
        purchase = user.purchases.get(message_id)
        if purchase is None:
            raise ValueError('purchase not existing')

        return user, purchase

    def process_message(self, telegram_update: MessageUpdate) -> bool:
        if self.check_user_id(telegram_update) is False:
            self.bot.send_message(telegram_update.message.chat.id, 'Not allowed to talk to strangers')

        if telegram_update.message.text == f'{Configuration.NEW_PURCHASE}':
            message = self.bot.send_message(telegram_update.message.chat.id, 'Enter purchase details:', reply_markup=create_inline_kb())
            user = self.db.get_user(telegram_update.message.chat.id)
            if user is None:
                user = self.db.create_user(telegram_update.message.chat.id)

            user.purchases[message.id] = Purchase(is_closed=False)  # Добавляем в покупку этот юзер ид

        elif telegram_update.message.text == '\start':
            start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button1 = types.KeyboardButton(Configuration.NEW_PURCHASE)
            start_markup.add(button1)
            self.bot.send_message(telegram_update.message.chat.id, text="Ready to make a purchase?", reply_markup=start_markup)

        else:
            user, purchase = self.get_user_and_purchase(telegram_update)
            if user.step is StepOfPurchase.write_price:
                self.add_price(telegram_update, user, purchase)

            elif user.step is StepOfPurchase.write_comment:
                self.add_comment(telegram_update, user, purchase)

            else:
                self.bot.send_message(telegram_update.message.chat.id, 'what is this? I dont understand')

        return True

    def add_comment(self, request, user: UserState, purchase: Purchase):
        purchase.name = request.message.text
        user.step = StepOfPurchase.default

        self.bot.edit_message_text(
            chat_id=request.message.chat.id,
            message_id=user.current_purchase,
            text="The comment has been entered. What's next?", reply_markup=create_inline_kb(purchase))

    def add_price(self, request, user: UserState, purchase: Purchase):
        purchase.price = request.message.text
        user.step = StepOfPurchase.default

        self.bot.edit_message_text(
            chat_id=request.message.chat.id,
            message_id=user.current_purchase,
            text="The price has been entered. What's next?",
            reply_markup=create_inline_kb(purchase))

    def choose_category(self, callback):
        self.bot.edit_message_text(
            chat_id=callback.callback_query.message.chat.id,
            message_id=callback.callback_query.message.message_id,
            reply_markup=choose_category_kb(),
            text='Choose category:'
        )

    def add_category(self, callback, _: UserState, purchase: Purchase):
        purchase.category = Category[callback.callback_query.data]
        self.bot.edit_message_text(
            chat_id=callback.callback_query.message.chat.id,
            message_id=callback.callback_query.message.message_id,
            text="The category has been entered. What's next?", reply_markup=create_inline_kb(purchase))

    def enter_price(self, callback, user: UserState, _: Purchase):
        user.step = StepOfPurchase.write_price
        user.current_purchase = callback.callback_query.message.message_id

        self.bot.send_message(callback.callback_query.message.chat.id, 'Enter price:')

    def enter_comment(self, callback, user: UserState, _):
        self.bot.send_message(callback.callback_query.message.chat.id, 'Enter comment:')
        user.step = StepOfPurchase.write_comment
        user.current_purchase = callback.callback_query.message.message_id

    def result(self, callback, _: UserState, purchase: Purchase):
        purchase.is_closed = True
        self.bot.edit_message_text(
            chat_id=callback.callback_query.message.chat.id,
            message_id=callback.callback_query.message.message_id,
            reply_markup=None,
            text=f'Purchase {purchase.name} \nCategory {purchase.category.value}\nPrice {purchase.price} RSD\ndone')
        sh = gc.open_by_key(Configuration.GOOGLE_TOKEN)
        sh.sheet1.append_row([purchase.category.value, purchase.price, purchase.name])
