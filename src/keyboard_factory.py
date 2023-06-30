
import typing as t

from pydantic.main import BaseModel

from src.config import Configuration
from src.data_objects import Purchase, Category
from src.pydantic_models import ReplyMarkup


# class ReplyMarkup(BaseModel):    # Модель
#     class Button(BaseModel):    # inline нужен тоолько в связке с reply, поэтому он внутри
#         text: str
#         callback_data: str
#
#     inline_keyboard: t.List[t.List[Button]]
#     row_width = 1


def kb_for_income(purchase: t.Optional[Purchase] = None) -> ReplyMarkup:
    button1 = ReplyMarkup.InlineKeyboard(text=Configuration.ADD_PRICE_KEY, callback_data=Configuration.ADD_PRICE_KEY)
    button2 = ReplyMarkup.InlineKeyboard(text=Configuration.ADD_COMMENT_KEY,
                                         callback_data=Configuration.ADD_COMMENT_KEY)
    button3 = ReplyMarkup.InlineKeyboard(text=Configuration.DONE_PURCHASE_KEY,
                                         callback_data=Configuration.DONE_PURCHASE_KEY)

    if purchase is not None:
        if purchase.price is not None:
            button1 = ReplyMarkup.InlineKeyboard(text=purchase.price, callback_data=Configuration.ADD_PRICE_KEY)

        if purchase.name is not None:
            button2 = ReplyMarkup.InlineKeyboard(text=purchase.name, callback_data=Configuration.ADD_COMMENT_KEY)

    return ReplyMarkup(inline_keyboard=[[button1], [button2], [button3]])


# Основная клав-ра, с которой будет происходить добавление покупок
def create_inline_kb(purchase: t.Optional[Purchase] = None) -> ReplyMarkup:
    button1 = ReplyMarkup.InlineKeyboard(text=Configuration.ADD_CATEGORY_KEY,
                                         callback_data=Configuration.ADD_CATEGORY_KEY)
    button2 = ReplyMarkup.InlineKeyboard(text=Configuration.ADD_PRICE_KEY, callback_data=Configuration.ADD_PRICE_KEY)
    button3 = ReplyMarkup.InlineKeyboard(text=Configuration.ADD_COMMENT_KEY,
                                         callback_data=Configuration.ADD_COMMENT_KEY)
    button4 = ReplyMarkup.InlineKeyboard(text=Configuration.DONE_PURCHASE_KEY,
                                         callback_data=Configuration.DONE_PURCHASE_KEY)

    if purchase is not None:
        if purchase.category is not None:
            button1 = ReplyMarkup.InlineKeyboard(text=purchase.category.value,
                                                 callback_data=Configuration.ADD_CATEGORY_KEY)
        if purchase.price is not None:
            button2 = ReplyMarkup.InlineKeyboard(text=purchase.price, callback_data=Configuration.ADD_PRICE_KEY)

        if purchase.name is not None:
            button3 = ReplyMarkup.InlineKeyboard(text=purchase.name, callback_data=Configuration.ADD_COMMENT_KEY)

    return ReplyMarkup(inline_keyboard=[[button1], [button2], [button3], [button4]])


def choose_category_kb() -> ReplyMarkup:
    category_markup = ReplyMarkup(inline_keyboard=[])
    categories = list(Category.__members__.values())

    for i in range(0, len(Category), 2):
        row = []
        row.append(ReplyMarkup.InlineKeyboard(text=f'{categories[i].value}', callback_data=categories[i].name))
        if i + 1 < len(Category):
            row.append(ReplyMarkup.InlineKeyboard(text=f'{categories[i + 1].value}', callback_data=categories[i + 1].name))
        category_markup.inline_keyboard.append(row)

    return category_markup
