import typing as t

from src.config import Configuration
from src.data_objects import Purchase, Category
from src.pydantic_models import InlineKeyboard, InlineMarkup


def kb_for_income(purchase: t.Optional[Purchase] = None) -> InlineMarkup:
    button1 = InlineKeyboard(text=Configuration.ADD_PRICE_KEY, callback_data=Configuration.ADD_PRICE_KEY)
    button2 = InlineKeyboard(text=Configuration.ADD_COMMENT_KEY,
                             callback_data=Configuration.ADD_COMMENT_KEY)
    button3 = InlineKeyboard(text=Configuration.DONE_PURCHASE_KEY,
                             callback_data=Configuration.DONE_PURCHASE_KEY)

    if purchase is not None:
        if purchase.price is not None:
            button1 = InlineKeyboard(text=purchase.price, callback_data=Configuration.ADD_PRICE_KEY)

        if purchase.name is not None:
            button2 = InlineKeyboard(text=purchase.name, callback_data=Configuration.ADD_COMMENT_KEY)

    return InlineMarkup(inline_keyboard=[[button1], [button2], [button3]])


# Основная клав-ра, с которой будет происходить добавление покупок
def create_inline_kb(purchase: t.Optional[Purchase] = None) -> InlineMarkup:
    button1 = InlineKeyboard(text=Configuration.ADD_CATEGORY_KEY,
                             callback_data=Configuration.ADD_CATEGORY_KEY)
    button2 = InlineKeyboard(text=Configuration.ADD_PRICE_KEY, callback_data=Configuration.ADD_PRICE_KEY)
    button3 = InlineKeyboard(text=Configuration.ADD_COMMENT_KEY,
                             callback_data=Configuration.ADD_COMMENT_KEY)
    button4 = InlineKeyboard(text=Configuration.DONE_PURCHASE_KEY,
                             callback_data=Configuration.DONE_PURCHASE_KEY)

    if purchase is not None:
        if purchase.category is not None:
            button1 = InlineKeyboard(text=purchase.category.value,
                                     callback_data=Configuration.ADD_CATEGORY_KEY)
        if purchase.price is not None:
            button2 = InlineKeyboard(text=purchase.price, callback_data=Configuration.ADD_PRICE_KEY)

        if purchase.name is not None:
            button3 = InlineKeyboard(text=purchase.name, callback_data=Configuration.ADD_COMMENT_KEY)

    return InlineMarkup(inline_keyboard=[[button1], [button2], [button3], [button4]])


def choose_category_kb() -> InlineMarkup:
    category_markup = InlineMarkup(inline_keyboard=[])
    categories = list(Category.__members__.values())

    for i in range(0, len(Category), 2):
        row = []
        row.append(InlineKeyboard(text=f'{categories[i].value}', callback_data=categories[i].name))
        if i + 1 < len(Category):
            row.append(InlineKeyboard(text=f'{categories[i + 1].value}', callback_data=categories[i + 1].name))
        category_markup.inline_keyboard.append(row)

    return category_markup
