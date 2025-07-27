import logging
from typing import Sequence, Optional

from sqlalchemy import select, func, or_
from sqlalchemy.exc import SQLAlchemyError

from infrastructure.database.models.accruals import Accrual
from infrastructure.database.repo.base import BaseRepo
from tgbot.services.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class AccrualRepo(BaseRepo):
    async def accruals_sum(self, user_id: int) -> int:
        """
        Расчёт суммы полученных пользователем достижений

        :param user_id: Идентификатор пользователя в Telegram
        :return: Сумма баллов всех полученных достижений
        """
        select_stmt = (
            select(func.sum(Accrual.Point)).where(Accrual.ChatId == user_id)
        )
        result = await self.session.execute(select_stmt)
        total = result.scalar()

        return total or 0

    async def user_accruals(
            self,
            user_id: Optional[int] = None,
            fullname: Optional[str] = None,
    ) -> Sequence[Accrual]:
        """
        Поиск начислений пользователя в БД по фильтрам

        Args:
            user_id: Уникальный идентификатор пользователя Telegram
            fullname: ФИО пользователя в БД

        Returns:
            Список объектов Accrual или пустой список
        """
        filters = []

        if user_id:
            filters.append(Accrual.ChatId == user_id)
        if fullname:
            filters.append(Accrual.FIO == fullname)

        if not filters:
            raise ValueError("At least one parameter must be provided to user_accruals()")

        # Combine all filters using OR
        query = select(Accrual).where(or_(*filters))

        try:
            result = await self.session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"[БД] Ошибка получения начислений пользователя: {e}")
            return []
