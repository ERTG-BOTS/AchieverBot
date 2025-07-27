from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.keyboards.user.main import MainMenu


class AwardsMenu(CallbackData, prefix='awards'):
    menu: str
    page: int = 1
    award_id: int = 0


class AvailableAwardsMenu(CallbackData, prefix="avail_awards"):
    action: str  # "page" or "select"
    page: int = 1
    award_id: int = 0


class AwardSelect(CallbackData, prefix="award_select"):
    award_id: int


def awards_kb() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="❇️ Доступные", callback_data=AwardsMenu(menu="available").pack()),
            InlineKeyboardButton(text="✴️ Использованные", callback_data=AwardsMenu(menu="executed").pack()),
        ],
        [
            InlineKeyboardButton(text="🏆 Все возможные", callback_data=AwardsMenu(menu="all").pack()),
        ],
        [
            InlineKeyboardButton(text="↩️ Назад", callback_data=MainMenu(menu="main").pack()),
        ]
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard


def awards_paginated_kb(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = []

    # Pagination row
    if total_pages > 1:
        pagination_row = []

        # Previous page button
        if current_page > 1:
            pagination_row.append(
                InlineKeyboardButton(
                    text="⬅️",
                    callback_data=AwardsMenu(menu="all", page=current_page - 1).pack()
                )
            )

        # Page indicator
        pagination_row.append(
            InlineKeyboardButton(
                text=f"{current_page}/{total_pages}",
                callback_data="noop"  # Non-functional button for display
            )
        )

        # Next page button
        if current_page < total_pages:
            pagination_row.append(
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=AwardsMenu(menu="all", page=current_page + 1).pack()
                )
            )

        buttons.append(pagination_row)

    # Navigation row
    navigation_row = [
        InlineKeyboardButton(text="↩️ Назад", callback_data=MainMenu(menu="awards").pack()),
        InlineKeyboardButton(text="🏠 Домой", callback_data=MainMenu(menu="main").pack()),
    ]
    buttons.append(navigation_row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def awards_available_kb(page_awards, current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Create keyboard with 2 award buttons per row + navigation"""
    buttons = []

    # Award selection buttons - 2 per row
    if page_awards:
        award_buttons = []
        for award in page_awards:
            award_buttons.append(
                InlineKeyboardButton(
                    text=f"🎁 {award.Name}",
                    callback_data=AwardSelect(award_id=award.Id).pack()
                )
            )

        # Split award buttons into rows of 2
        for i in range(0, len(award_buttons), 2):
            row = award_buttons[i:i + 2]
            buttons.append(row)

    # Pagination row
    if total_pages > 1:
        pagination_row = []

        # Previous page button
        if current_page > 1:
            pagination_row.append(
                InlineKeyboardButton(
                    text="⬅️",
                    callback_data=AvailableAwardsMenu(action="page", page=current_page - 1).pack()
                )
            )

        # Page indicator
        pagination_row.append(
            InlineKeyboardButton(
                text=f"{current_page}/{total_pages}",
                callback_data="noop"  # Non-functional button
            )
        )

        # Next page button
        if current_page < total_pages:
            pagination_row.append(
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=AvailableAwardsMenu(action="page", page=current_page + 1).pack()
                )
            )

        buttons.append(pagination_row)

    # Navigation row
    navigation_row = [
        InlineKeyboardButton(text="↩️ Назад", callback_data=MainMenu(menu="awards").pack()),
        InlineKeyboardButton(text="🏠 Домой", callback_data=MainMenu(menu="main").pack()),
    ]
    buttons.append(navigation_row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def awards_back() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="↩️ Назад", callback_data=MainMenu(menu="awards").pack()),
            InlineKeyboardButton(text="🏠 Домой", callback_data=MainMenu(menu="main").pack()),
        ]
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard


def confirm_award_kb(award_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="✨ Активировать", callback_data=AwardsMenu(menu="confirm", award_id=award_id).pack()),
        ],
        [
            InlineKeyboardButton(text="↩️ Назад", callback_data=AwardsMenu(menu="available").pack()),
            InlineKeyboardButton(text="🏠 Домой", callback_data=MainMenu(menu="main").pack()),
        ]
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard