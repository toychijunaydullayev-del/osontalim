# Ro'yxatdan o'tish Telegram boti

O'qituvchilarni ro'yxatga oluvchi, majburiy obunani tekshiruvchi va
ma'lumotlarni adminga yuboruvchi Telegram bot (aiogram 3, SQLite).

## Bot nima qiladi

1. `/start` bosilganda, foydalanuvchi belgilangan kanal(lar)ga obuna bo'lganmi tekshiradi.
   Obuna bo'lmasa — kanal havolasi va "✅ Obunani tekshirish" tugmasi chiqadi.
2. `/register` buyrug'i bilan ro'yxatdan o'tish boshlanadi, ketma-ket so'raladi:
   - Qayerdansiz (viloyat/shahar)
   - Qaysi fan
   - Ism familiya
   - Ish tajribasi (necha yil)
   - Sertifikat rasmi
   - Diplom rasmi
   - Telefon raqam (tugma orqali yoki qo'lda)
3. Yakunida ma'lumotlar SQLite bazaga yoziladi va ikkala rasm (sertifikat + diplom)
   barcha ma'lumotlar bilan birga har bir adminga yuboriladi.
4. Adminlar uchun buyruqlar:
   - `/stats` — jami ro'yxatdan o'tganlar soni
   - `/list` — so'nggi ro'yxatlar (oxirgi 20 tasi)
   - `/export` — SQLite baza faylini (`.db`) to'g'ridan-to'g'ri Telegram orqali yuboradi
   - `/export_excel` — barcha ro'yxatlarni `.xlsx` (Excel) faylga aylantirib yuboradi

## O'rnatish

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` faylini oching va quyidagilarni to'ldiring:

- `BOT_TOKEN` — @BotFather dan olingan token
- `ADMIN_IDS` — admin(lar)ning Telegram ID raqami(lari), vergul bilan ajratilgan
  (o'z ID'ingizni bilish uchun @userinfobot ga yozing)
- `CHANNEL_ID` — majburiy obuna kanali (`@kanal_username` yoki `-100...` ID)
- `CHANNEL_TITLE`, `CHANNEL_URL` — kanal nomi va havolasi

### MUHIM: bot kanalda ADMIN bo'lishi shart

Majburiy obunani tekshirish ishlashi uchun botni obuna talab qilinadigan
kanalga **administrator** qilib qo'shish kerak (kamida "foydalanuvchilarni
ko'rish" huquqi bilan). Aks holda obuna tekshiruvi doim "obuna emas" deb
qaytaradi.

Bir nechta kanal talab qilmoqchi bo'lsangiz, `config.py` faylidagi
`REQUIRED_CHANNELS` ro'yxatiga yana bir dict qo'shing.

## Ishga tushirish

```bash
python bot.py
```

## Fayllar tuzilishi

```
telegram_bot/
├── bot.py                  # asosiy fayl, botni ishga tushiradi
├── config.py                # sozlamalar (.env dan o'qiydi)
├── states.py                 # FSM holatlari
├── database.py               # SQLite bilan ishlash
├── keyboards.py               # tugmalar
├── handlers/
│   ├── registration.py          # ro'yxatdan o'tish jarayoni
│   ├── admin.py                  # /stats, /list
│   └── subscription.py            # obuna tekshiruvi
├── requirements.txt
├── .env.example
└── README.md
```

## Bazadagi ma'lumotlarni qanday yuklab olish mumkin

**1-yo'l (eng oson) — bot ichidan:**
Telegramda botga admin sifatida yozing:
- `/export_excel` — Excel faylini yuboradi, Excel/Google Sheets'da ochiladi (tavsiya etiladi)
- `/export` — xom `.db` faylini yuboradi (DB Browser for SQLite bilan ochiladi)

**2-yo'l — serverdan to'g'ridan-to'g'ri:**
Agar botni serverda (VPS) ishlatayotgan bo'lsangiz, `bot_database.db` faylini
kompyuteringizga ko'chirib oling:
```bash
scp user@server_ip:/path/to/telegram_bot/bot_database.db ./
```
Keyin uni **DB Browser for SQLite** (bepul, https://sqlitebrowser.org) yordamida
oching yoki Python/pandas orqali o'qing:
```python
import sqlite3, pandas as pd
conn = sqlite3.connect("bot_database.db")
df = pd.read_sql_query("SELECT * FROM users", conn)
df.to_excel("royxat.xlsx", index=False)
```

## Railway'ga joylashtirish (deploy)

1. Loyihani GitHub'ga yuklang (yangi repo yarating, `git init`, `git add .`,
   `git commit -m "init"`, `git push`). `.env` fayli `.gitignore` tufayli
   yuklanmaydi — bu to'g'ri, tokenni GitHub'ga qo'ymang.
2. [railway.app](https://railway.app) da **New Project → Deploy from GitHub repo**
   ni tanlab, shu repo'ni ulang.
3. Railway loyihasida **Variables** bo'limiga o'ting va `.env.example` dagi
   barcha o'zgaruvchilarni (`BOT_TOKEN`, `ADMIN_IDS`, `CHANNEL_ID` va h.k.) qo'lda kiriting.
4. Railway `Procfile`'ni ko'rib, botni **worker** sifatida ishga tushiradi
   (bu web server emas, shuning uchun alohida port ochish shart emas).
5. **MUHIM — ma'lumotlar bazasi uchun Volume qo'shing:** Railway'da fayl
   tizimi har bir yangi deploy'da tozalanadi, ya'ni Volume bo'lmasa
   `bot_database.db` yo'qolib qoladi. Railway loyihangizda
   **Settings → Volumes → New Volume** orqali masalan `/data` yo'liga volume
   biriktiring, so'ng Variables'ga `DB_PATH=/data/bot_database.db` qo'shing.

Shundan so'ng bot avtomatik ishga tushadi va har safar GitHub'ga push
qilganingizda Railway o'zi qayta deploy qiladi.

## Eslatmalar

- Ma'lumotlar `bot_database.db` (SQLite) faylida saqlanadi. Ko'p foydalanuvchi
  kutilsa, PostgreSQL kabi bazaga o'tish tavsiya etiladi.
- Rasm fayllar Telegram serverida saqlanadi, bot faqat `file_id` ni bazaga yozadi.
- Botni doimiy ishlatish uchun serverga joylashtirib, `systemd`, `pm2` yoki
  `screen`/`tmux` orqali fon jarayon sifatida ishga tushiring.
