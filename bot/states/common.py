from aiogram.fsm.state import State, StatesGroup


class SearchState(StatesGroup):
    choosing_type = State()
    choosing_filters = State()
    searching = State()


class PromoState(StatesGroup):
    waiting_code = State()


class SupportState(StatesGroup):
    waiting_message = State()
