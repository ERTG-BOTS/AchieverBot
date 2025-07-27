from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.repo.accruals import AccrualRepo
from infrastructure.database.repo.awards import AwardsRepo
from infrastructure.database.repo.buffer import BufferRepo
from infrastructure.database.repo.executes import ExecutesRepo
from infrastructure.database.repo.users import UserRepo


@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def users(self) -> UserRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return UserRepo(self.session)

    @property
    def accruals(self) -> AccrualRepo:
        """
        The Accrual repository sessions are required to manage accrual operations.
        """
        return AccrualRepo(self.session)

    @property
    def awards(self) -> AwardsRepo:
        """
        The Awards repository sessions are required to manage awards operations.
        """
        return AwardsRepo(self.session)

    @property
    def executes(self) -> ExecutesRepo:
        """
        The Executes repository sessions are required to manage executes operations.
        """
        return ExecutesRepo(self.session)

    @property
    def buffer(self) -> BufferRepo:
        """
        The Buffer repository sessions are required to manage buffer operations.
        """
        return BufferRepo(self.session)