import abc
import json
import typing as t
from datetime import date

import requests
from requests.models import Response
from telebot import types
from pydantic import BaseModel, parse_obj_as

from src.config import Configuration, gc
from src.data_objects import UserState, Category, Purchase, StepOfPurchase
from src.keyboard_factory import create_inline_kb, choose_category_kb, kb_for_income, ReplyMarkup
from src.pydantic_models import TelegramUpdate, CallbackUpdate, MessageUpdate, SendMessageResponse


class Processor(abc.ABC):

    def process(self, telegram_update: TelegramUpdate):
        raise NotImplementedError


class MessageProcessor(Processor):
    __SEND_MESSAGE_URL = f"https://api.telegram.org/bot{Configuration.TG_TOKEN}/sendMessage"
    __UPDATE_MESSAGE_URL = f"https://api.telegram.org/bot{Configuration.TG_TOKEN}/editMessageText"

    def __init__(self, db):
        self.db = db

    def process(self, telegram_update: TelegramUpdate):
        if isinstance(telegram_update, CallbackUpdate):
            self.__process_callback(telegram_update)
        elif isinstance(telegram_update, MessageUpdate):
            self.__process_message(telegram_update)

    def __check_user_id(self, telegram_update: TelegramUpdate) -> bool:
        if isinstance(telegram_update, MessageUpdate):
            chat_id = telegram_update.message.chat.id
        elif isinstance(telegram_update, CallbackUpdate):
            chat_id = telegram_update.callback_query.message.chat.id
        else:
            return False

        return chat_id in Configuration.USERS

    def __process_callback(self, callback: CallbackUpdate):
        if self.__check_user_id(callback):
            user, purchase = self.__get_user_and_purchase(callback)
            if callback.callback_query.data == Configuration.NEW_PURCHASE:
                message = self.__send_message(
                    callback.callback_query.message.chat.id,
                    'Введите детали покупки:',
                    reply_markup=create_inline_kb()
                )

                purchase = Purchase(is_closed=False)
                user.purchases[message.result.message_id] = purchase
                user.current_purchase = message.result.message_id

            if callback.callback_query.data == Configuration.ADD_PRICE_KEY:
                self.__enter_price(callback, user, purchase)
            if callback.callback_query.data == Configuration.ADD_CATEGORY_KEY:
                self.__choose_category(callback)
            if callback.callback_query.data == Configuration.DONE_PURCHASE_KEY:
                self.__result(callback, user, purchase)
            if callback.callback_query.data == Configuration.ADD_COMMENT_KEY:
                self.__enter_comment(callback, user, purchase)
            if callback.callback_query.data in Category.__members__:
                self.__add_category(callback, user, purchase)
        else:
            self.__send_message(callback.callback_query.message.chat.id, 'Не могу с вами общаться. Я вас не знаю')

    def __get_user_and_purchase(self, telegram_update: TelegramUpdate) -> t.Tuple[UserState, Purchase]:
        if isinstance(telegram_update, MessageUpdate):
            chat_id = telegram_update.message.chat.id
            user = self.db.get_user(chat_id)
            message_id = telegram_update.message.message_id
        elif isinstance(telegram_update, CallbackUpdate):
            chat_id = telegram_update.callback_query.message.chat.id
            user = self.db.get_user(chat_id)
            message_id = telegram_update.callback_query.message.message_id
        else:
            raise ValueError('Invalid object')

        if user is None:
            raise ValueError('user is None')

        purchase = user.purchases.get(user.current_purchase)
        if purchase is None:
            raise ValueError('No purchase with current id')

        return user, purchase

    def __process_message(self, telegram_update: MessageUpdate) -> bool:
        if self.__check_user_id(telegram_update) is False:
            self.__send_message(telegram_update.message.chat.id, 'Не могу с вами общаться. Я вас не знаю')

        if telegram_update.message.text == f'{Configuration.INCOME}':
            message = self.__send_message(telegram_update.message.chat.id, 'Введите поступивший доход:',
                                          reply_markup=kb_for_income())
            user = self.db.get_user(telegram_update.message.chat.id)
            if user is None:
                user = self.db.create_user(telegram_update.message.chat.id)

            user.purchases[message.result.message_id] = Purchase(category=Category.income, is_closed=False)


        elif telegram_update.message.text == '/start':
            button1 = ReplyMarkup.InlineKeyboard(text=Configuration.NEW_PURCHASE, callback_data=Configuration.NEW_PURCHASE)
            button2 = ReplyMarkup.InlineKeyboard(text=Configuration.INCOME, callback_data=Configuration.INCOME)
            start_markup = ReplyMarkup(inline_keyboard=[[button1, button2]])

            message = self.__send_message(chat_id=telegram_update.message.chat.id, text="Что мне сделать?",
                                reply_markup=start_markup)

            user = self.db.get_user(telegram_update.message.chat.id)

            if user is None:
                user = self.db.create_user(telegram_update.message.chat.id)

            user.purchases[message.result.message_id] = Purchase(is_closed=False)

        else:
            user, purchase = self.__get_user_and_purchase(telegram_update)
            if user.step is StepOfPurchase.write_price:
                self.__add_price(telegram_update, user, purchase)

            elif user.step is StepOfPurchase.write_comment:
                self.__add_comment(telegram_update, user, purchase)
            else:
                self.__send_message(telegram_update.message.chat.id, 'Что это? Я не понимаю')

        return True

    def __add_comment(self, request, user: UserState, purchase: Purchase):
        purchase.name = request.message.text
        user.step = StepOfPurchase.default
        self.__edit_message_text(chat_id=request.message.chat.id,
                                 message_id=user.current_purchase,
                                 text="Комментарий добавлен. Что дальше?", reply_markup=create_inline_kb(purchase))
        print(user.current_purchase)
        print(purchase)

    def __add_price(self, request, user: UserState, purchase: Purchase):
        print(f'price {request}')
        if request.message.text.isdigit():
            purchase.price = request.message.text
            user.step = StepOfPurchase.default
            self.__edit_message_text(chat_id=request.message.chat.id,
                                     message_id=user.current_purchase,
                                     text="Сумма была добавлена. Что дальше?",
                                     reply_markup=create_inline_kb(purchase)
                                     )
            print(user.current_purchase)
            print(purchase)
        else:
            self.__send_message(request.message.chat.id, 'Неверный формат ввода цены. Попробуйте снова.')

    def __choose_category(self, callback):
        reply_markup = choose_category_kb()
        print(reply_markup)
        self.__edit_message_text(chat_id=callback.callback_query.message.chat.id,
                                 message_id=callback.callback_query.message.message_id,
                                 reply_markup=choose_category_kb(),
                                 text='Выберите категорию:')

    def __add_category(self, callback, _: UserState, purchase: Purchase):
        purchase.category = Category[callback.callback_query.data]
        self.__edit_message_text(chat_id=callback.callback_query.message.chat.id,
                                 message_id=callback.callback_query.message.message_id,
                                 text="Категория была добавлена. Что дальше?",
                                 reply_markup=create_inline_kb(purchase))

    def __enter_price(self, callback: CallbackUpdate, user: UserState, _: Purchase):
        user.step = StepOfPurchase.write_price
        user.current_purchase = callback.callback_query.message.message_id
        print(user.current_purchase)

        self.__send_message(callback.callback_query.message.chat.id, 'Введите сумму:')

    def __send_message(self, chat_id: int, text: str, reply_markup: t.Optional[ReplyMarkup] = None) -> SendMessageResponse:
        body = {
            "chat_id": chat_id,
            "text": text,
        }
        if reply_markup is not None:
            body['reply_markup'] = reply_markup.dict()

        response = requests.post(
            url=self.__SEND_MESSAGE_URL,
            json=body
        )
        return parse_obj_as(SendMessageResponse, response.json())


    def __edit_message_text(self, chat_id: int, message_id: int, text: str,  reply_markup: t.Optional[ReplyMarkup] = None) -> SendMessageResponse:
        body = {
            "chat_id": chat_id,
            "text": text,
            "message_id": message_id,
        }

        if reply_markup is not None:
            body['reply_markup'] = reply_markup.dict()

        response = requests.post(
            url=self.__UPDATE_MESSAGE_URL,
            json=body
        )
        return parse_obj_as(SendMessageResponse, response.json())

    def __enter_comment(self, callback, user: UserState, _: Purchase):
        user.step = StepOfPurchase.write_comment
        user.current_purchase = callback.callback_query.message.message_id
        print(user.current_purchase)
        self.__send_message(callback.callback_query.message.chat.id, 'Введите комментарий:')

    def __result(self, callback, user: UserState, purchase: Purchase):
        print(f'result {purchase}')
        purchase.is_closed = True
        user.current_purchase = callback.callback_query.message.message_id
        current_date = date.today().strftime("%m.%Y")
        self.__edit_message_text(chat_id=callback.callback_query.message.chat.id,
                                 message_id=callback.callback_query.message.message_id,
                                 reply_markup=None,
                                 text=f'Комментарий: {purchase.name} \nКатегория: {purchase.category.value}\nСумма: {purchase.price} RSD\nГотово')
        # log_sheet = gc.open_by_key(Configuration.GOOGLE_TOKEN)
        # log_sheet.sheet1.append_row(
        #     [str(current_date), purchase.category.value, str(purchase.price), purchase.name])
        #
        # budget_sheet = gc.open_by_key(Configuration.GOOGLE_TOKEN_BUDGET_TABLE)
        # worksheet = budget_sheet.sheet1
        # column = worksheet.find(str(current_date)).col
        # row = worksheet.find(purchase.category.value).row
        # cell = worksheet.cell(row, column)  # для получения объекта Cell по координатам
        # value = cell.value  # для получения значения ячейки или его изменения
        #
        # if value is None:
        #     value = 0
        # else:
        #     value = int(cell.value)
        #
        # value += int(purchase.price)
        # worksheet.update_cell(row, column, value)
