from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.keyboards.user.main import MainMenu


class AchievementsMenu(CallbackData, prefix='achievements'):
    menu: str
    page: int = 1


def achievements_kb() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🔎 Детализация", callback_data=AchievementsMenu(menu="details").pack()),
        ],
        [
            InlineKeyboardButton(text="🏆 Все возможные", callback_data=AchievementsMenu(menu="all").pack()),
        ],
        [
            InlineKeyboardButton(text="↩️ Назад", callback_data=MainMenu(menu="main").pack()),
        ]
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard