import logging
import re

from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from infrastructure.database.models import User
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.admin.main import AdminMenu
from tgbot.services.logger import setup_logging
from aiogram.fsm.context import FSMContext

search_router = Router()
search_router.message.filter(AdminFilter())

config = load_config(".env")

setup_logging()
logger = logging.getLogger(__name__)


class SearchState(StatesGroup):
    fio = State()


@search_router.callback_query(AdminMenu.filter(F.menu == "search"))
async def admin_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(f"""<b>🔎 Поиск сотрудника</b>

Введи полные или частичные фио специалиста для поиска""")
    await state.set_state(SearchState.fio)


@search_router.message(SearchState.fio)
async def search_message(message: Message, state: FSMContext, stp_db):
    fio = message.text.strip()
    await state.clear()

    # Регулярные выражения для определения полноты ввода
    regex_fullname = r"^([а-яА-ЯёЁ]+)\s([а-яА-ЯёЁ]+)\s([а-яА-ЯёЁ]+)\s([а-яА-ЯёЁ]+)$" #
    regex_name_surname_patronymic = r"^([а-яА-ЯёЁ]+)\s([а-яА-ЯёЁ]+)\s([а-яА-ЯёЁ]+)$"
    regex_name_surname = r"^([а-яА-ЯёЁ]+)\s([а-яА-ЯёЁ]+)$" # Имя + Фамилия

    async with stp_db() as session:
        repo = RequestsRepo(session)

        # Сначала пробуем точный поиск
        user: User = await repo.users.get_user(fullname=fio)

    if user:
        # Найден точный match
        logger.info(f"[Админ] - [Поиск пользователя] {user.FIO}")
        await message.answer(f"Пользователь найден: {user.FIO}")
        # TODO добавить обработку найденного пользователя
        return

    # Если точного совпадения нет, пробуем частичный поиск
    if re.match(regex_fullname, fio) or re.match(regex_name_surname_patronymic, fio):
        # Полное ФИО введено, но точного совпадения нет
        users = await repo.users.get_users_by_fio_parts(fio)

        if users:
            if len(users) == 1:
                await message.answer(f"""<b>🔎 Поиск сотрудника</b>"

Найден пользователь: {users[0].FIO}
""")
                # Обработка найденного пользователя
            else:
                # Несколько совпадений — показываем список для выбора
                response = "Найдено несколько пользователей:\n"
                for i, user in enumerate(users, 1):
                    response += f"{i}. {user.FIO}\n"
                await message.answer(response)
                # Здесь можно добавить логику выбора из списка
        else:
            await message.answer("Пользователь не найден")

    elif re.match(regex_name_surname, fio):
        # Введены только имя и фамилия — используем частичный поиск
        users = await repo.users.get_users_by_fio_parts(fio)

        if users:
            if len(users) == 1:
                await message.answer(f"Найден пользователь: {users[0].FIO}")
                # Обработка найденного пользователя
            else:
                # Несколько совпадений
                response = "Найдено несколько пользователей. Уточните запрос:\n"
                for i, user in enumerate(users, 1):
                    response += f"{i}. {user.FIO}\n"
                await message.answer(response)
        else:
            await message.answer("Пользователи не найдены. Попробуйте ввести полное ФИО")

    else:
        # Некорректный формат ввода
        await message.answer(
            "Неверный формат ФИО. Введите в формате:\n"
            "• Имя Фамилия\n"
            "• Имя Фамилия Отчество\n"
            "• Имя Фамилия Отчество Дополнение"
        )