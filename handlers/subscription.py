from aiogram import Bot

from config import REQUIRED_CHANNELS


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    """Foydalanuvchi barcha majburiy kanallarga obuna bo'lganmi, shuni tekshiradi.

    MUHIM: bot tekshirilayotgan kanal(lar)da ADMIN bo'lishi shart,
    aks holda get_chat_member xatolik qaytaradi.
    """
    for ch in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch["chat_id"], user_id=user_id)
            if member.status in ("left", "kicked"):
                return False
        except Exception:
            # Bot kanalda admin emas yoki kanal topilmadi — xavfsizlik uchun False
            return False
    return True
