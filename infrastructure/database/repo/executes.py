from datetime import datetime, timedelta

from sqlalchemy import select, func

from infrastructure.database.models import User
from infrastructure.database.models.awards import Awards
from infrastructure.database.models.executes import Execute
from infrastructure.database.repo.awards import AwardsRepo
from infrastructure.database.repo.base import BaseRepo
from tgbot.misc.roles import executed_codes


class ExecutesRepo(BaseRepo):
    async def executes_sum(self, user_id: int) -> int:
        """
        Расчёт суммы потраченных пользователем баллов

        :param user_id: Идентификатор пользователя в Telegram
        :return: Сумма потраченных баллов на награды
        """
        select_stmt = (
            select(func.sum(Execute.Executing)).where(Execute.ChatId == user_id)
        )
        result = await self.session.execute(select_stmt)
        total = result.scalar()

        return total or 0


    async def add_pending_award(self, award: Awards, user: User, comment: str) -> Execute:
        """
        Добавление награды, запись в таблицу Executes

        Args:
            award: Объект модели Awards
            user: Объект модели User
            comment: Комментарий к награде
        """

        insert_stmt = Execute(
            ChatId=user.ChatId,
            FIO=user.FIO,
            Name=award.Name,
            Executing=executed_codes[award.Interaction],
            Position=user.Position,
            Count=0,
            TargetCount=award.Count,
            Date=datetime.now() + timedelta(hours=5),
            Comment=comment
        )

        self.session.add(insert_stmt)
        await self.session.commit()
        await self.session.refresh(insert_stmt)
        return insert_stmt

    # async def is_award_used_today(self, award_name: int, fio: str):
    #     select_stmt = select().where(Execute.FIO == fio, Execute.Count >= Execute.TargetCount, Execute.Name == award_name, Execute.Executing / 7 < 2)