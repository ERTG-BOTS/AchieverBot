from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Integer, BigInteger, Column, NVARCHAR, Unicode
from sqlalchemy import text, BIGINT, Boolean, true
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TableNameMixin


class Execute(Base, TableNameMixin):
    """
    Класс, представляющий сущность начисления в БД.

    Attributes:
        Id (Mapped[int]): Уникальный идентификатор пользователя.
        Name (Mapped[str]): Название достижения.
        FIO (Mapped[int]): ФИО пользователя.
        Name (Mapped[str]): Название полученной награды.
        Executing (Mapped[str]): Кол-во потраченных на награду баллов.
        Position (Mapped[str]): Должность пользователя.
        Count [Mapped[int]): Кол-во применений награды.
        TargetCount [Mapped[int]): Кол-во доступных применений награды.
        Date [Mapped[datetime]): Дата приобретения награды.
        ExecutingDate [Mapped[datetime]): Дата последней активации награды.
        WhoExecuting [Mapped[str]): Кто активировал награду.
        Comment [Mapped[str]): Комментарий к активации награды.

    Methods:
        __repr__(): Returns a string representation of the User object.

    Inherited Attributes:
        Inherits from Base and TableNameMixin classes, which provide additional attributes and functionality.

    Inherited Methods:
        Inherits methods from Base and TableNameMixin classes, which provide additional functionality.

    """
    __tablename__ = 'Executed'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    ChatId = Column(BigInteger, nullable=False)
    FIO = Column(Unicode(255), nullable=False)
    Name = Column(Unicode(255), nullable=False)
    Executing = Column(Integer, nullable=False)
    Position = Column(Unicode(255), nullable=False)
    Count = Column(Integer, nullable=False)
    TargetCount = Column(Integer, nullable=False)
    Date = Column(DATETIME2, nullable=False)
    ExecutingDate = Column(DATETIME2, nullable=True)
    WhoExecuting = Column(Unicode(255), nullable=True)
    Comment = Column(Unicode, nullable=True)

    def __repr__(self):
        return f"<Execute {self.Id} {self.ChatId} {self.FIO} {self.Name} {self.Executing} {self.Position} {self.Count} {self.TargetCount} {self.Date} {self.ExecutingDate} {self.WhoExecuting}>"
