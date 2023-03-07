import dataclasses
import enum
import typing as t


class Category(enum.Enum):
    cafe = 1
    food = 2


@dataclasses.dataclass
class Purchase:
    is_closed: bool
    category: t.Optional[Category] = None
    price: t.Optional[int] = None
    name: t.Optional[str] = None
