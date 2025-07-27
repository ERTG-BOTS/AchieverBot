import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from infrastructure.database.models import User
from infrastructure.database.models.awards import Awards
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.config import load_config
from tgbot.handlers.user.main import main_cmd
from tgbot.keyboards.user.awards import AwardsMenu, awards_kb, AvailableAwardsMenu, \
    awards_available_kb, awards_paginated_kb, AwardSelect, awards_back, confirm_award_kb
from tgbot.keyboards.user.main import MainMenu
from tgbot.misc.states import AwardBuy
from tgbot.services.logger import setup_logging
from tgbot.services.mailing import new_award_email

awards_router = Router()

config = load_config(".env")

setup_logging()
logger = logging.getLogger(__name__)


@awards_router.callback_query(MainMenu.filter(F.menu == "awards"))
async def awards(callback: CallbackQuery):
    """
    Обработчик клика на меню наград
    """
    await callback.answer()
    await callback.message.edit_text(f"""<b>👏 Награды</b>

📌<u><b>Награды</b></u> - это бонус за заработанные баллы

Список доступных наград можно посмотреть по кнопке <b>❇️ Доступные</b>, там указаны их описания и стоимость
Награды со счетчиком 🧮 можно использовать <u>один раз за смену</u>

После активации награда идет на рассмотрение ответственным
Статус можно узнать в меню <b>✴️ Использованные</b>""", reply_markup=awards_kb())
    logging.info(
        f"[Пользователь] - [Меню] {callback.from_user.username} ({callback.from_user.id}): Открыто меню наград")


@awards_router.callback_query(AwardsMenu.filter(F.menu == "available"))
async def awards_available(callback: CallbackQuery, achiever_db) -> None:
    """
    Обработчик клика на меню доступных пользователю наград
    """
    await callback.answer()
    await show_available_awards_page(callback, achiever_db, page=1)


@awards_router.callback_query(AvailableAwardsMenu.filter(F.action == "page"))
async def awards_available_page_handler(callback: CallbackQuery, callback_data: AvailableAwardsMenu,
                                        achiever_db):
    """
    Обработчик смены страниц в списке доступных пользователю наград
    """
    await callback.answer()
    await show_available_awards_page(callback, achiever_db, page=callback_data.page)


@awards_router.callback_query(AwardSelect.filter())
async def award_select_handler(callback: CallbackQuery, callback_data: AwardSelect, achiever_db, stp_db):
    """
    Обработчик выбора награды из списка доступных по клику на клавиатуру
    """
    await callback.answer()
    async with achiever_db() as session:
        repo = RequestsRepo(session)
        total_points = await repo.accruals.accruals_sum(user_id=callback.from_user.id)
        wasted_points = await repo.executes.executes_sum(user_id=callback.from_user.id)
        user_balance = total_points - wasted_points

        available_awards = await repo.awards.get_available_awards(
            user_id=callback.from_user.id,
            user_balance=user_balance
        )

    # Валидация выбора награды
    selected_award = next((award for award in available_awards if award.Id == callback_data.award_id), None)

    if not selected_award:
        await callback.answer("❌ Награда не найдена или больше недоступна")
        return

    if selected_award.Sum > user_balance:
        await callback.answer(f"❌ Недостаточно очков! Нужно: {selected_award.Sum}, у вас: {user_balance}")
        return

    async with achiever_db() as achiever_session:
        repo = RequestsRepo(achiever_session)
        db_selected_award: Awards = await repo.awards.get_award(award_id=selected_award.Id)

    if db_selected_award.IsShiftDependent:
        async with stp_db() as stp_session:
            repo = RequestsRepo(stp_session)
            user: User = await repo.users.get_user(user_id=callback.from_user.id)
            is_working = await repo.buffer.is_user_working_today(fio=user.FIO, division=user.Division)

        if not is_working:
            await callback.answer("❌ Награда доступна только в основные рабочие\доп смены!")
            return

    await callback.message.edit_text(f"""<b>👏 Активация награды</b>

Ты выбрал награду <b>{db_selected_award.Name}</b>
Активируем?

<blockquote expandable><b>✨ Стоимость:</b> {db_selected_award.Sum} баллов
<b>📝 Описание:</b> {db_selected_award.Description}
<b>🧮 Активаций:</b> {db_selected_award.Count}</blockquote>

<i>После активации у тебя останется <b>{user_balance - db_selected_award.Sum} баллов</b></i>""",
                                     reply_markup=confirm_award_kb(award_id=db_selected_award.Id))
    logging.info(
        f"[Пользователь] {callback.from_user.username} ({callback.from_user.id}): Выбрана награда {db_selected_award.Name}, ждем подтверждение")


@awards_router.callback_query(AwardsMenu.filter(F.award_id != 0))
async def confirm_award(callback: CallbackQuery, callback_data: AwardsMenu, state: FSMContext, achiever_db):
    await callback.answer()
    async with achiever_db() as achiever_session:
        repo = RequestsRepo(achiever_session)
        db_selected_award: Awards = await repo.awards.get_award(award_id=callback_data.award_id)

    await callback.message.edit_text(f"""<b>👏 Подтверждение покупки</b>

Готов выдать тебе награду <b>{db_selected_award.Name}</b>
Напиши комментарий к покупке награды и отправь в этот чат

<blockquote expandable><b>✨ Стоимость:</b> {db_selected_award.Sum} баллов
<b>📝 Описание:</b> {db_selected_award.Description}
<b>🧮 Активаций:</b> {db_selected_award.Count}</blockquote>""",
                                     reply_markup=awards_back())
    await state.update_data(award_id=db_selected_award.Id)
    await state.set_state(AwardBuy.comment)
    logging.info(
        f"[Пользователь] - [Покупка награды] {callback.from_user.username} ({callback.from_user.id}): Подтвержден выбор награды {db_selected_award.Name}, ждем комментарий")


@awards_router.message(AwardBuy.comment)
async def comment_award(message: Message, state: FSMContext, achiever_db, stp_db):
    await message.delete()
    state_data = await state.get_data()

    async with stp_db() as achiever_session:
        repo = RequestsRepo(achiever_session)
        user: User = await repo.users.get_user(message.from_user.id)
        boss: User = await repo.users.get_user(fullname=user.Boss)

    async with achiever_db() as achiever_session:
        repo = RequestsRepo(achiever_session)
        award: Awards = await repo.awards.get_award(award_id=state_data["award_id"])

        user_accruals = await repo.accruals.accruals_sum(user_id=message.from_user.id)
        user_executes = await repo.executes.executes_sum(user_id=message.from_user.id)
        user_balance = user_accruals - user_executes  # before current execute

    execute = await repo.executes.add_pending_award(award=award, user=user, comment=message.text)
    await new_award_email(execute=execute, award=award, user=user, boss=boss)
    await message.bot.send_sticker(chat_id=message.from_user.id,
                                   sticker="CAACAgIAAxkBAAEMIzVmR3nXp5DuvWwCgMOPLIIuvmcYcwACjkQAAm44QErJPrDwaCwLDDUE")
    await message.bot.edit_message_text(chat_id=message.from_user.id, message_id=message.message_id - 1, text=f"""<b>✅️ Награда приобретена</b>

Ты купил награду <b>{award.Name}</b>

<blockquote expandable><b>✨ Стоимость:</b> {award.Sum} баллов
<b>📝 Описание:</b> {award.Description}
<b>🧮 Активаций:</b> {award.Count}</blockquote>

<b>🗑️ Потрачено:</b> {award.Sum} баллов
<b>💳 Осталось:</b> {user_balance - award.Sum} баллов

<i>Награда находится на рассмотрении
По результату <b>тебе придет уведомление</b></i>""")

    logging.info(
        f"[Пользователь] - [Покупка награды] {message.from_user.username} ({message.from_user.id}): Приобретена награда {award.Name}")
    await main_cmd(message=message, state=state, stp_db=stp_db)


# Обработчик отображения всех возможных наград
@awards_router.callback_query(AwardsMenu.filter(F.menu == "all"))
async def awards_all(callback: CallbackQuery, achiever_db):
    """
    Обработчик клика на меню всех возможных наград
    """

    # Достаём номер страницы из callback data, стандартно = 1
    callback_data = AwardsMenu.unpack(callback.data)
    page = getattr(callback_data, 'page', 1)

    async with achiever_db() as session:
        repo = RequestsRepo(session)
        all_awards = await repo.awards.get_awards()

    # Логика пагинации
    awards_per_page = 5
    total_awards = len(all_awards)
    total_pages = (total_awards + awards_per_page - 1) // awards_per_page

    # Считаем начало и конец текущей страницы
    start_idx = (page - 1) * awards_per_page
    end_idx = start_idx + awards_per_page
    page_awards = all_awards[start_idx:end_idx]

    # Построение списка наград для текущей страницы
    awards_list = []
    for counter, award in enumerate(page_awards, start=start_idx + 1):
        awards_list.append(f"""{counter}. <b>{award.Name}</b>
💵 Стоимость: {award.Sum}
📝 Описание: {award.Description}""")
        if award.Count > 0:
            awards_list.append(f"""🧮 Активаций: {award.Count}""")
        awards_list.append("")

    message_text = f"""<b>🏆 Все возможные награды</b>
<i>Страница {page} из {total_pages}</i>

{"\n".join(awards_list)}"""

    await callback.message.edit_text(
        message_text,
        reply_markup=awards_paginated_kb(page, total_pages)
    )
    logging.info(
        f"[Пользователь] - [Меню] {callback.from_user.username} ({callback.from_user.id}): Открыто меню всех наград, страница {page}")


async def show_available_awards_page(callback: CallbackQuery, achiever_db, page: int = 1):
    """
    Функция-хелпер для отображения доступных пользователю наград
    """
    async with achiever_db() as session:
        repo = RequestsRepo(session)
        total_points = await repo.accruals.accruals_sum(user_id=callback.from_user.id)
        wasted_points = await repo.executes.executes_sum(user_id=callback.from_user.id)
        user_balance = total_points - wasted_points

        available_awards = await repo.awards.get_available_awards(
            user_id=callback.from_user.id,
            user_balance=user_balance
        )

    # Логика пагинации
    awards_per_page = 5
    total_awards = len(available_awards)
    total_pages = (total_awards + awards_per_page - 1) // awards_per_page if total_awards > 0 else 1

    # Убеждаемся, что страница существует
    page = max(1, min(page, total_pages))

    # Считаем начало и конец текущей страницы
    start_idx = (page - 1) * awards_per_page
    end_idx = start_idx + awards_per_page
    page_awards = available_awards[start_idx:end_idx]

    # Построение списка наград для текущей страницы
    awards_list = []
    for counter, award in enumerate(page_awards, start=start_idx + 1):
        awards_list.append(f"""{counter}. <b>{award.Name}</b>
💵 Стоимость: {award.Sum}
📝 Описание: {award.Description}""")
        if hasattr(award, 'Count') and award.Count > 0:
            awards_list.append(f"""🧮 Активаций: {award.Count}""")
        awards_list.append("")

    if total_awards == 0:
        message_text = f"""<b>❇️ Доступные награды</b>
💰 Ваш баланс: {user_balance} очков

Пока нет доступных наград."""
    else:
        message_text = f"""<b>❇️ Доступные награды</b>
💰 Ваш баланс: {user_balance} очков
<i>Страница {page} из {total_pages}</i>

{"\n".join(awards_list)}"""

    await callback.message.edit_text(message_text, reply_markup=awards_available_kb(page_awards, page, total_pages))
    logging.info(
        f"[Пользователь] - [Меню] {callback.from_user.username} ({callback.from_user.id}): Открыто меню доступных наград, страница {page}")
