from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from states import Registration
from keyboards import phone_keyboard, subscription_keyboard, remove_keyboard
from handlers.subscription import is_subscribed
from database import add_registration
from config import ADMIN_IDS

router = Router()


async def send_welcome(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "Ushbu bot orqali o'qituvchilar ro'yxatdan o'tadi.\n\n"
        "Ro'yxatdan o'tishni boshlash uchun /register buyrug'ini yuboring."
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    if not await is_subscribed(bot, message.from_user.id):
        await message.answer(
            "Botdan foydalanish uchun quyidagi kanal(lar)ga obuna bo'ling, "
            "so'ngra \"✅ Obunani tekshirish\" tugmasini bosing:",
            reply_markup=subscription_keyboard(),
        )
        return
    await send_welcome(message, state)


@router.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if await is_subscribed(bot, callback.from_user.id):
        await callback.message.delete()
        await send_welcome(callback.message, state)
    else:
        await callback.answer("❌ Siz hali barcha kanallarga obuna bo'lmadingiz!", show_alert=True)


@router.message(Command("register"))
async def cmd_register(message: Message, state: FSMContext, bot: Bot):
    if not await is_subscribed(bot, message.from_user.id):
        await message.answer(
            "Avval kanal(lar)ga obuna bo'ling:",
            reply_markup=subscription_keyboard(),
        )
        return
    await state.set_state(Registration.region)
    await message.answer(
        "📍 Qayerdansiz? (Viloyat/tuman/shahar nomini yozing)",
        reply_markup=remove_keyboard(),
    )


@router.message(Registration.region)
async def process_region(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Iltimos, matn ko'rinishida yozing.")
        return
    await state.update_data(region=message.text.strip())
    await state.set_state(Registration.subject)
    await message.answer("📚 Qaysi fan bo'yicha mutaxassissiz?")


@router.message(Registration.subject)
async def process_subject(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Iltimos, matn ko'rinishida yozing.")
        return
    await state.update_data(subject=message.text.strip())
    await state.set_state(Registration.full_name)
    await message.answer("🧑‍🏫 Ism va familiyangizni to'liq kiriting:")


@router.message(Registration.full_name)
async def process_full_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Iltimos, matn ko'rinishida yozing.")
        return
    await state.update_data(full_name=message.text.strip())
    await state.set_state(Registration.experience)
    await message.answer("📅 Necha yillik ish tajribangiz bor? (masalan: 3)")


@router.message(Registration.experience)
async def process_experience(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("Iltimos, faqat raqam kiriting (masalan: 5).")
        return
    await state.update_data(experience=message.text.strip())
    await state.set_state(Registration.certificate)
    await message.answer("🖼 Sertifikat rasmini yuboring (rasm sifatida, fayl emas):")


@router.message(Registration.certificate, F.photo)
async def process_certificate(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(certificate_file_id=file_id)
    await state.set_state(Registration.diploma)
    await message.answer("🎓 Diplom rasmini yuboring (rasm sifatida, fayl emas):")


@router.message(Registration.certificate)
async def process_certificate_invalid(message: Message):
    await message.answer("Iltimos, sertifikat rasmini rasm (photo) ko'rinishida yuboring.")


@router.message(Registration.diploma, F.photo)
async def process_diploma(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(diploma_file_id=file_id)
    await state.set_state(Registration.phone)
    await message.answer(
        "📞 Telefon raqamingizni yuboring (tugma orqali yoki qo'lda kiriting):",
        reply_markup=phone_keyboard(),
    )


@router.message(Registration.diploma)
async def process_diploma_invalid(message: Message):
    await message.answer("Iltimos, diplom rasmini rasm (photo) ko'rinishida yuboring.")


@router.message(Registration.phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext, bot: Bot):
    await finish_registration(message, state, bot, message.contact.phone_number)


@router.message(Registration.phone, F.text)
async def process_phone_text(message: Message, state: FSMContext, bot: Bot):
    digits = "".join(c for c in message.text.strip() if c.isdigit() or c == "+")
    if len(digits) < 9:
        await message.answer("Iltimos, telefon raqamni to'g'ri kiriting yoki tugma orqali yuboring.")
        return
    await finish_registration(message, state, bot, digits)


async def finish_registration(message: Message, state: FSMContext, bot: Bot, phone: str):
    data = await state.get_data()
    data["telegram_id"] = message.from_user.id
    data["username"] = message.from_user.username or "-"
    data["phone"] = phone

    add_registration(data)

    await message.answer(
        "✅ Rahmat! Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n"
        "Ma'lumotlaringiz administratorga yuborildi.",
        reply_markup=remove_keyboard(),
    )

    caption = (
        "🆕 <b>Yangi ro'yxatdan o'tish</b>\n\n"
        f"👤 Ism familiya: {data.get('full_name')}\n"
        f"📍 Manzil: {data.get('region')}\n"
        f"📚 Fan: {data.get('subject')}\n"
        f"📅 Ish tajribasi: {data.get('experience')} yil\n"
        f"📞 Telefon: {data.get('phone')}\n"
        f"🆔 Telegram ID: {data.get('telegram_id')}\n"
        f"🔗 Username: @{data.get('username')}"
    )

    media = [
        InputMediaPhoto(media=data["certificate_file_id"], caption=caption, parse_mode="HTML"),
        InputMediaPhoto(media=data["diploma_file_id"]),
    ]

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_media_group(chat_id=admin_id, media=media)
        except Exception:
            pass

    await state.clear()
