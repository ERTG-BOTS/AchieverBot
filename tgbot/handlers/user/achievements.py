from aiogram import Router, F
from aiogram.types import CallbackQuery

from tgbot.config import load_config
from tgbot.keyboards.user.achievements import achievements_kb
from tgbot.keyboards.user.main import MainMenu

achievements_router = Router()

config = load_config(".env")


@achievements_router.callback_query(MainMenu.filter(F.menu == "achievements"))
async def achievements(callback: CallbackQuery):
    """
    Обработчик клика на меню ачивок
    """
    await callback.message.edit_text(f"""<b>🎯 Ачивки</b>

📌<u><b>Ачивки</b></u> - достижения за успехи в работе, за которые начисляются баллы
Бывают <b>автоматические</b> и <b>ручные</b> (начисляются администратором)""", reply_markup=achievements_kb())