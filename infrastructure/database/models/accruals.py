from typing import Optional

from sqlalchemy import String, Unicode, Integer
from sqlalchemy import text, BIGINT, Boolean, true
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TableNameMixin


class Accrual(Base, TableNameMixin):
    """
    Класс, представляющий сущность начисления в БД.

    Attributes:
        Id (Mapped[int]): Уникальный идентификатор пользователя.
        ChatId (Mapped[Optional[str]]): Идентификатор чата с пользователем в Telegram.
        FIO (Mapped[str]): ФИО пользователя.
        Name (Mapped[str]): Название достижения.
        TargetKPI (Mapped[str]): KPI пользователя при получении достижения.
        Point (Mapped[int]): Кол-во баллов, начисленных пользователю за достижение.
        Period (Mapped[int]): Период/частота начисления достижения.
        Date (Mapped[int]): Дата получения достижения.

    Methods:
        __repr__(): Returns a string representation of the User object.

    Inherited Attributes:
        Inherits from Base and TableNameMixin classes, which provide additional attributes and functionality.

    Inherited Methods:
        Inherits methods from Base and TableNameMixin classes, which provide additional functionality.

    """
    # TODO заменить название таблицы в БД на accruals
    __tablename__ = 'accurals'

    Id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    ChatId: Mapped[int] = mapped_column(BIGINT, nullable=False)
    FIO: Mapped[str] = mapped_column(Unicode(255), nullable=False)
    Name: Mapped[str] = mapped_column(String(255), nullable=False)
    TargetKPI: Mapped[str] = mapped_column(String(255), nullable=False)
    Point: Mapped[int] = mapped_column(Integer, nullable=False)
    Period: Mapped[str] = mapped_column(String(255), nullable=False)
    Date: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self):
        return f"<Accrual {self.Id} {self.ChatId} {self.Name} {self.TargetKPI} {self.Point} {self.Period} {self.Date}>"
