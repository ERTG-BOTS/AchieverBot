from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from infrastructure.database.models import User
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.config import load_config
from tgbot.keyboards.user.main import user_kb, MainMenu, back_kb

user_router = Router()

config = load_config(".env")


@user_router.message(CommandStart())
async def main_cmd(message: Message, state: FSMContext, stp_db):
    async with stp_db() as session:
        repo = RequestsRepo(session)
        user: User = await repo.users.get_user(user_id=message.from_user.id)

    state_data = await state.get_data()

    if user:
        await message.answer_sticker(
            sticker="CAACAgIAAxkBAAEMCf5mM0yOPIO3B7VADqT6-c8Lmhi-oQACH0YAAmAamUnQNXBXD5yG_DQE"
        )
        await message.answer(
            f"""Привет, <b>{user.FIO}</b>!

Я - Ачивер
Помогу тебе получить награды и бонусы за твои KPI!

<i>Используй меню для управление ботом</i>""",
            reply_markup=user_kb(
                role=int(state_data.get("role"))
                if state_data.get("role")
                else user.Role,
                is_role_changed=True if state_data.get("role") else False,
            ),
        )
    else:
        await message.answer(f"""Привет, <b>@{message.from_user.username}</b>!
        
Не нашел тебя в списке зарегистрированных пользователей

Регистрация происходит через бота Графиков
Если возникли сложности с регистраций обратись к МиП""")


@user_router.callback_query(MainMenu.filter(F.menu == "main"))
async def main_cb(callback: CallbackQuery, stp_db, state: FSMContext):
    async with stp_db() as session:
        repo = RequestsRepo(session)
        user: User = await repo.users.get_user(user_id=callback.from_user.id)

    state_data = await state.get_data()

    await callback.message.edit_text(
        f"""Привет, <b>{user.FIO}</b>!

Я - Ачивер
Помогу тебе получить награды и бонусы за твои KPI!

Используй меню, чтобы выбрать действие""",
        reply_markup=user_kb(
            role=int(state_data.get("role")) if state_data.get("role") else user.Role,
            is_role_changed=True if state_data.get("role") else False,
        ),
    )


@user_router.callback_query(MainMenu.filter(F.menu == "level"))
async def user_level(callback: CallbackQuery, achiever_db):
    async with achiever_db() as session:
        repo = RequestsRepo(session)
        total_points = await repo.accruals.accruals_sum(user_id=callback.from_user.id)
        wasted_points = await repo.executes.executes_sum(user_id=callback.from_user.id)

    current_points_amount = total_points - wasted_points

    # TODO уточнить механику расчета уровня
    await callback.message.edit_text(
        f"""<b>🏅 Профиль</b>

Текущее кол-во баллов: <b>{current_points_amount}</b>
Уровень: <b>{round(total_points / 100)}</b>

<i>Всего накоплено: <b>{total_points}</b>
Всего потрачено: <b>{wasted_points}</b></i>""",
        reply_markup=back_kb(),
    )


@user_router.callback_query(MainMenu.filter(F.menu == "faq"))
async def user_level(callback: CallbackQuery):
    await callback.message.edit_text(
        """<b>❓️ FAQ</b>

📌<u><b>Ачивки</b></u> - достижения за успехи в работе, за которые начисляются баллы
Бывают <b>автоматические</b> и <b>ручные</b> (начисляются администратором)
Полный список в меню <b>🎯 Достижения</b>

В <b>🏅 Профиле</b> можно посмотреть историю получения ачивок и баллов
У периодических ачивок указывается период начисления, у остальных - конкретный день

📌<u><b>Награда</b></u> - бонус за заработанные баллы
Список в меню <b>❇️ Доступные</b> с описанием и стоимостью
Награды со счетчиком 🧮 можно использовать <u>один раз за смену</u>

После активации награда идет на рассмотрение ответственным
Статус можно узнать в меню <b>✴️ Использованные</b>

❗️️ О багах можно сообщить по кнопке <b>🙋‍♂️ Помогите</b>""",
        reply_markup=back_kb(),
    )
