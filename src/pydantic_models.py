import typing as t

from pydantic import BaseModel


class Chat(BaseModel):
    id: int


class InlineKeyboard(BaseModel):
    text: str
    callback_data: t.Optional[str]


class ReplyKeyboard(BaseModel):
    text: str


class ReplyMarkup(BaseModel):
    keyboard: t.List[t.List[ReplyKeyboard]]
    one_time_keyboard: t.Optional[bool] = False
    resize_keyboard: t.Optional[bool] = False


class InlineMarkup(BaseModel):
    inline_keyboard: t.List[t.List[InlineKeyboard]]


class UserMessage(BaseModel):
    message_id: int
    chat: Chat
    date: int
    text: str
    reply_markup: t.Optional[InlineMarkup]


class CallbackUpdate(BaseModel):
    class Query(BaseModel):
        id: str
        message: UserMessage
        data: str

    callback_query: Query


class MessageUpdate(BaseModel):
    message: UserMessage


TelegramUpdate = t.Union[MessageUpdate, CallbackUpdate]


class SendMessageResponse(BaseModel):
    class Result(BaseModel):
        message_id: int

    result: t.Optional[Result]
