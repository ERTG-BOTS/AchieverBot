from typing import Optional

from sqlalchemy import String, Integer, Unicode
from sqlalchemy import text, BIGINT, Boolean, true
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TableNameMixin


class Awards(Base, TableNameMixin):
    """
    Класс, представляющий сущность начисления в БД.

    Attributes:
        Id (Mapped[int]): Уникальный идентификатор пользователя.
        Name (Mapped[str]): Название награды.
        Sum (Mapped[int]): Стоимость награды.
        Interaction (Mapped[str]): Роль для взаимодействия.
        Count (Mapped[int]): Кол-во доступных использований награды после приобретения.
        Description (Mapped[str]): Описание награды.
        IsShiftDependent (Mapped[bool]): Зависимость применения награды от наличия смены.

    Methods:
        __repr__(): Returns a string representation of the User object.

    Inherited Attributes:
        Inherits from Base and TableNameMixin classes, which provide additional attributes and functionality.

    Inherited Methods:
        Inherits methods from Base and TableNameMixin classes, which provide additional functionality.

    """
    __tablename__ = "Awards"


    Id: Mapped[int] = mapped_column(Integer, primary_key=True)
    Name: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    Sum: Mapped[int] = mapped_column(Integer, nullable=False)
    Interaction: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    Count: Mapped[int] = mapped_column(Integer, nullable=False)
    Description: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    IsShiftDependent: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return (f"<Awards(Id={self.Id}, Name='{self.Name}', Sum={self.Sum}, "
                f"Interaction='{self.Interaction}', Count={self.Count}, "
                f"Description='{self.Description}', IsShiftDependent={self.IsShiftDependent})>")
