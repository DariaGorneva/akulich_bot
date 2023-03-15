import typing as t
from telebot.types import Message, CallbackQuery
from config import Configuration
from database import Database
from functools import wraps


def check_purchase_middleware(db: Database):
    def decorator(func: t.Callable):
        @wraps(func)
        def wrapper(obj: t.Union[Message, CallbackQuery]):
            if type(obj) is Message:
                # get chat/message id from message
                user = db.get_user(obj.chat.id)
                message_id = user.current_purchase
            elif type(obj) is CallbackQuery:
                # get chat/message id from callback
                user = db.get_user(obj.message.chat.id)
                message_id = obj.message.id
            else:
                raise Exception('Invalid object')

            # check user
            if user is None:
                raise Exception('user is None')
            # check purchase
            purchase = user.purchases.get(message_id)
            if purchase is None:
                raise Exception('purchase not existing')
            # run handler
            return func(obj, user, purchase)

        return wrapper

    return decorator


def check_user_id(message):  # проверка юзер ид
    user_id = message.from_user.id
    if user_id not in Configuration.USERS:
        return True
