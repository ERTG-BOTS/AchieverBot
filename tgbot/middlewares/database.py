import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.exc import OperationalError, DBAPIError, DisconnectionError

from infrastructure.database.models import User
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.config import Config
from tgbot.services.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class DatabaseMiddleware(BaseMiddleware):
    def __init__(
        self, config: Config, main_session_pool, achiever_session_pool
    ) -> None:
        self.main_session_pool = main_session_pool
        self.achiever_session_pool = achiever_session_pool
        self.config = config

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Use separate sessions for different databases
                async with self.main_session_pool() as main_session:
                    async with self.achiever_session_pool() as achiever_session:
                        # Создаем репозитории для разных БД
                        main_repo = RequestsRepo(main_session)  # Для БД STPMain
                        achiever_repo = RequestsRepo(
                            achiever_session
                        )  # Для БД AchieverBot

                        user: User = await main_repo.users.get_user(
                            user_id=event.from_user.id
                        )

                        # Add data to the context
                        data["main_session"] = main_session
                        data["main_repo"] = main_repo
                        data["achiever_session"] = achiever_session
                        data["achiever_repo"] = achiever_repo
                        data["user"] = user

                        return await handler(event, data)

            except (OperationalError, DBAPIError, DisconnectionError) as e:
                retry_count += 1
                logger.warning(
                    f"[Middleware] Database connection error, повтор {retry_count}/{max_retries}: {e}"
                )

                if retry_count >= max_retries:
                    logger.error(
                        f"[Middleware] Все попытки подключения к БД исчерпаны: {e}"
                    )
                    if hasattr(
                        event, "reply"
                    ):  # Check if it's a message that can be replied to
                        try:
                            await event.reply(
                                "⚠️ Временные проблемы с базой данных. Попробуйте позже."
                            )
                        except:
                            pass
                    return None

                # Continue the retry loop
                continue

            except Exception as e:
                logger.error(f"[Middleware] Неожиданная ошибка: {e}")
                return None

        # This should not be reached, but just in case
        return None
