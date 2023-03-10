import dataclasses
import enum
import typing as t


class Category(enum.Enum):  # заранее известны категории покупок
    cafe = 1
    subscriptions = 2
    household = 3
    beauty = 4
    health = 5
    entertainment = 6
    documentation = 7
    holidays = 8
    transport = 9
    rent = 10
    food = 11


@dataclasses.dataclass
class Purchase:     # здесь храним информацию о пользователе и покупке
    is_closed: bool
    category: t.Optional[Category] = None
    price: t.Optional[str] = None
    name: t.Optional[str] = None
