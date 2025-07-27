from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, and_, extract

from infrastructure.database.models.awards import Awards
from infrastructure.database.models.executes import Execute
from infrastructure.database.repo.base import BaseRepo


class AwardsRepo(BaseRepo):
    async def get_awards(self):
        """
        Получаем полный список наград
        """

        select_stmt = select(Awards)

        result = await self.session.execute(select_stmt)
        awards = result.scalars().all()

        return list(awards)

    async def get_award(self, award_id: int) -> Optional[Awards]:
        """
        Получение информации о награде по ее идентификатору

        Args:
            award_id: Уникальный идентификатор награды в таблице Awards
        """

        select_stmt = select(Awards).where(Awards.Id == award_id)
        result = await self.session.execute(select_stmt)

        return result.scalar_one()

    async def get_available_awards(self, user_id: int, user_balance: int) -> List[Awards]:
        """
        Получаем список наград, которые:
        1. Имеют название
        2. Стоимость награды меньше или равна кол-ву очков пользователя
        """

        # Проверка использования награды в текущем месяце неактуальна
        # Получаем список наград, активированных в этом месяце
        # current_month = datetime.now().month
        #
        # executed_awards_subquery = (
        #     select(Execute.Name)
        #     .where(
        #         and_(
        #             Execute.ChatId == user_id,
        #             Execute.TargetCount == Execute.Count,
        #             extract('month', Execute.Date) == current_month
        #         )
        #     )
        # )

        # Получаем список наград, подходящих под критерии
        select_stmt = (
            select(Awards)
            .where(
                and_(
                    Awards.Name.isnot(None),
                    Awards.Sum <= user_balance,
                    # Awards.Name.notin_(executed_awards_subquery)
                )
            )
        )

        result = await self.session.execute(select_stmt)
        awards = result.scalars().all()

        return list(awards)
