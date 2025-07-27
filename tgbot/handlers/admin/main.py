import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from infrastructure.database.models import User
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.user.main import main_cb
from tgbot.keyboards.admin.main import AdminMenu, ChangeRole, admin_kb
from tgbot.keyboards.user.main import user_kb
from tgbot.misc.roles import role_names
from tgbot.services.logger import setup_logging

admin_router = Router()
admin_router.message.filter(AdminFilter())

config = load_config(".env")

setup_logging()
logger = logging.getLogger(__name__)


@admin_router.message(CommandStart())
async def admin_start(message: Message, user: User, state: FSMContext):
    state_data = await state.get_data()

    if "role" in state_data:
        logging.info(
            f"[Админ] {message.from_user.username} ({message.from_user.id}): Открыто меню пользователя"
        )
        await message.answer(
            f"""Привет, <b>{user.FIO}</b>!

Я - Ачивер
Помогу тебе получить награды и бонусы за твои KPI!

Используй меню, чтобы выбрать действие""",
            reply_markup=user_kb(
                role=int(state_data.get("role"))
                if state_data.get("role")
                else user.Role,
                is_role_changed=True if state_data.get("role") else False,
            ),
        )
        return

    logging.info(
        f"[Админ] {message.from_user.username} ({message.from_user.id}): Открыто админ-меню"
    )
    await message.answer(
        f"""Привет, <b>{user.FIO}</b>!

<b>🎭 Твоя роль:</b> {role_names[user.Role]}

<i>Используй меню для управления ботом</i>""",
        reply_markup=admin_kb(),
    )


@admin_router.callback_query(ChangeRole.filter())
async def change_role(
    callback: CallbackQuery, callback_data: ChangeRole, state: FSMContext, user: User
) -> None:
    await callback.answer()

    match callback_data.role:
        case "mip":
            await state.update_data(role=6)  # Мониторинг и прогнозирование (МИП)
            logging.info(
                f"[Админ] {callback.from_user.username} ({callback.from_user.id}): Роль изменена с {user.Role} на 6"
            )
        case "gok":
            await state.update_data(role=5)  # Группа оценки качества
            logging.info(
                f"[Админ] {callback.from_user.username} ({callback.from_user.id}): Роль изменена с {user.Role} на 5"
            )
        case "duty":
            await state.update_data(role=3)  # Старший (не руководитель группы)
            logging.info(
                f"[Админ] {callback.from_user.username} ({callback.from_user.id}): Роль изменена с {user.Role} на 3"
            )
        case "spec":
            await state.update_data(role=1)  # Специалист
            logging.info(
                f"[Админ] {callback.from_user.username} ({callback.from_user.id}): Роль изменена с {user.Role} на 1"
            )

    await main_cb(callback, user, state)


@admin_router.callback_query(AdminMenu.filter(F.menu == "reset"))
async def reset_role(callback: CallbackQuery, state: FSMContext, stp_db):
    """
    Сброс кастомной роли через клавиатуру
    """
    state_data = await state.get_data()
    await state.clear()

    async with stp_db() as session:
        repo = RequestsRepo(session)
        user: User = await repo.users.get_user(user_id=callback.from_user.id)

    logging.info(
        f"[Админ] Пользователь {callback.from_user.username} ({callback.from_user.id}): Роль изменена с {state_data.get('role')} на {user.Role} кнопкой"
    )

    await callback.message.edit_text(
        f"""Привет, <b>{user.FIO}</b>!

<b>🎭 Твоя роль:</b> {role_names[user.Role]}

<i>Используй меню для управления ботом</i>""",
        reply_markup=admin_kb(),
    )


@admin_router.message(Command("reset"))
async def reset_role(message: Message, state: FSMContext, stp_db) -> None:
    """
    Сброс кастомной роли через команду
    """
    state_data = await state.get_data()
    await state.clear()

    async with stp_db() as session:
        repo = RequestsRepo(session)
        user: User = await repo.users.get_user(user_id=message.from_user.id)

    logging.info(
        f"[Админ] {message.from_user.username} ({message.from_user.id}): Роль изменена с {state_data.get('role')} на {user.Role} командой"
    )

    await message.answer(
        f"""Привет, <b>{user.FIO}</b>!

<b>🎭 Твоя роль:</b> {role_names[user.Role]}

<i>Используй меню для управления ботом</i>""",
        reply_markup=admin_kb(),
    )
