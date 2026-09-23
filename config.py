import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Admin(lar)ning Telegram ID raqamlari, vergul bilan ajratilgan
# Masalan: ADMIN_IDS=123456789,987654321
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# Majburiy obuna kanal(lar)i.
# chat_id: @username yoki -100... ko'rinishidagi ID (bot kanalda ADMIN bo'lishi shart!)
# url: foydalanuvchi bosadigan taklif havolasi
REQUIRED_CHANNELS = [
    {
        "chat_id": os.getenv("CHANNEL_ID", "@your_channel"),
        "title": os.getenv("CHANNEL_TITLE", "Bizning kanal"),
        "url": os.getenv("CHANNEL_URL", "https://t.me/your_channel"),
    },
]

DB_PATH = os.getenv("DB_PATH", "bot_database.db")
