from aiogram.fsm.state import State, StatesGroup


class OrderState(StatesGroup):
    phone = State()
    province = State()
    address = State()
    size_type = State()
    size = State()
    quantity = State()
    color = State()
    manual_price = State()
    note = State()
    photos = State()


class DesignState(StatesGroup):
    waiting_photo = State()