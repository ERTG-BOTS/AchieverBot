from aiogram.fsm.state import StatesGroup, State


class AdminChangeRole(StatesGroup):
    role = State()


class AwardBuy(StatesGroup):
    agree = State()
    comment = State()