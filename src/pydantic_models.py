from pydantic import BaseModel
import typing


class Chat(BaseModel):
    id: int


class ReplyMarkup(BaseModel):
    class InlineKeyboard(BaseModel):
        text: str
        callback_data: typing.Optional[str]

    inline_keyboard: typing.List[typing.List[InlineKeyboard]]



class UserMessage(BaseModel):
    message_id: int
    chat: Chat
    date: int
    text: str
    reply_markup: typing.Optional[ReplyMarkup]


class CallbackUpdate(BaseModel):
    class Query(BaseModel):
        id: str
        message: UserMessage
        data: str
    callback_query: Query


class MessageUpdate(BaseModel):
    message: UserMessage


TelegramUpdate = typing.Union[MessageUpdate, CallbackUpdate]


class SendMessageResponse(BaseModel):
    class Result(BaseModel):
        message_id: int

    result: typing.Optional[Result]
