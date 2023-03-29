from telebot import types
import typing as t
from src.config import Configuration
from src.data_objects import Purchase, Category


def kb_for_income(purchase: t.Optional[Purchase] = None) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton(text=Configuration.ADD_PRICE_KEY, callback_data=Configuration.ADD_PRICE_KEY)
    button2 = types.InlineKeyboardButton(text=Configuration.ADD_COMMENT_KEY,
                                         callback_data=Configuration.ADD_COMMENT_KEY)
    button3 = types.InlineKeyboardButton(text=Configuration.DONE_PURCHASE_KEY,
                                         callback_data=Configuration.DONE_PURCHASE_KEY)

    if purchase is not None:
        if purchase.price is not None:
            button1 = types.InlineKeyboardButton(text=purchase.price, callback_data=Configuration.ADD_PRICE_KEY)

        if purchase.name is not None:
            button2 = types.InlineKeyboardButton(text=purchase.name, callback_data=Configuration.ADD_COMMENT_KEY)

    markup.add(button1, button2, button3)
    return markup


# Основная клав-ра, с которой будет происходить добавление покупок
def create_inline_kb(purchase: t.Optional[Purchase] = None) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton(text=Configuration.ADD_CATEGORY_KEY,
                                         callback_data=Configuration.ADD_CATEGORY_KEY)
    button2 = types.InlineKeyboardButton(text=Configuration.ADD_PRICE_KEY, callback_data=Configuration.ADD_PRICE_KEY)
    button3 = types.InlineKeyboardButton(text=Configuration.ADD_COMMENT_KEY,
                                         callback_data=Configuration.ADD_COMMENT_KEY)
    button4 = types.InlineKeyboardButton(text=Configuration.DONE_PURCHASE_KEY,
                                         callback_data=Configuration.DONE_PURCHASE_KEY)

    if purchase is not None:
        if purchase.category is not None:
            button1 = types.InlineKeyboardButton(text=purchase.category.value,
                                                 callback_data=Configuration.ADD_CATEGORY_KEY)
        if purchase.price is not None:
            button2 = types.InlineKeyboardButton(text=purchase.price, callback_data=Configuration.ADD_PRICE_KEY)

        if purchase.name is not None:
            button3 = types.InlineKeyboardButton(text=purchase.name, callback_data=Configuration.ADD_COMMENT_KEY)

    markup.add(button1, button2, button3, button4)
    return markup


def choose_category_kb() -> types.InlineKeyboardMarkup:
    category_markup = types.InlineKeyboardMarkup(row_width=2)

    temp_array = []

    for category in Category:
        bbt = types.InlineKeyboardButton(f'{category.value}', callback_data=category.name)
        temp_array.append(bbt)

        if len(temp_array) == 2:
            category_markup.row(*temp_array)
            temp_array = []

    if len(temp_array) == 1:
        category_markup.row(temp_array[0])

    return category_markup
