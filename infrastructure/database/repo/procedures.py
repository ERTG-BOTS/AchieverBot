from typing import Optional

from sqlalchemy import select

from infrastructure.database.models import User
from infrastructure.database.repo.base import BaseRepo


class ProceduresRepo(BaseRepo):
    async def run_procedure(self, proc_name):
        proc_stmt = (
            f"EXEC {proc_name}"
        )
        result = await self.session.execute(proc_stmt)
        return result.scalar_one_or_none()
