import dataclasses
import enum
import typing as t


class Category(enum.Enum):  # заранее известны категории покупок
    cafe = 'кафе'
    subscriptions = 'подписки'
    household = 'бытовые расходы'
    beauty = 'красота'
    health = 'здоровье'
    entertainment = 'развлечения'
    documentation = 'документы'
    holidays = 'праздники'
    transport = 'транспорт'
    rent = 'аренда'
    food = 'еда необходимая'


@dataclasses.dataclass
class Purchase:     # здесь храним информацию о пользователе и покупке
    is_closed: bool
    category: t.Optional[Category] = None
    price: t.Optional[str] = None
    name: t.Optional[str] = None


class StepOfPurchase(enum.Enum):  # шаг, на котором находится юзер
    write_price = 1
    write_comment = 2
    default = 3


@dataclasses.dataclass
class UserState:    # состояние юзера - его шаг и общая информация о покупке // current_purchase нужна для того,
    # чтобы не потерять введённую цену или коммент
    step: StepOfPurchase = StepOfPurchase.default
    purchases: t.Dict[int, Purchase] = dataclasses.field(default_factory=lambda: dict())  # ?
    current_purchase: t.Optional[int] = None  # ?
