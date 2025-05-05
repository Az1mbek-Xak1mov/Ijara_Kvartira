from aiogram.fsm.state import State, StatesGroup

class StepByStepStates(StatesGroup):
    start = State()
    main = State()
    settings = State()
    back_setting = State()
    back_main = State()
    new_phone=State()

class OwnerState(StatesGroup):
    chat_id=State()
    fullname = State()
    phone_number = State()

class RenterState(StatesGroup):
    chat_id=State()
    fullname = State()
    phone_number = State()

class ApartmentState(StatesGroup):
    owner_id=State()
    district=State()
    price=State()
    type=State()
    floor=State()
    repair=State()
    images=State()
    rooms=State()
    description=State()
    phone_number=State()
    status=State()

class SearchState(StatesGroup):
    district = State()
    start_price = State()
    end_price = State()
    rooms=State()


class RoleState(StatesGroup):
    role=State()
