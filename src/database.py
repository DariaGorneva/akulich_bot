import typing as t
from src.data_objects import UserState


class Database:
    def __init__(self):
        self.__users: t.Dict[int, UserState] = {}

    def get_user(self, user_id: int) -> t.Optional[UserState]:
        return self.__users.get(user_id, None)

    def create_user(self, user_id: int) -> UserState:
        obj = UserState()
        self.__users[user_id] = obj
        return obj
