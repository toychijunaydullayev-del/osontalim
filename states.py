from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    region = State()        # Qayerdansiz
    subject = State()       # Qaysi fan
    full_name = State()     # Ism familya
    experience = State()    # Ish tajribasi (necha yil)
    certificate = State()   # Sertifikat rasmi
    diploma = State()       # Diplom rasmi
    phone = State()         # Telefon raqam
