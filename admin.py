import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from config import ADMIN_IDS, DB_PATH
from database import get_all_registrations, count_registrations

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    total = count_registrations()
    await message.answer(f"📊 Jami ro'yxatdan o'tganlar: {total} ta")


@router.message(Command("list"))
async def cmd_list(message: Message):
    if not is_admin(message.from_user.id):
        return
    rows = get_all_registrations()
    if not rows:
        await message.answer("Hozircha hech kim ro'yxatdan o'tmagan.")
        return

    for row in rows[:20]:
        text = (
            f"🆔 {row['id']} | {row['full_name']}\n"
            f"📍 {row['region']} | 📚 {row['subject']}\n"
            f"📅 Tajriba: {row['experience']} yil\n"
            f"📞 {row['phone']}\n"
            f"👤 tg_id: {row['telegram_id']} (@{row['username']})"
        )
        await message.answer(text)

    if len(rows) > 20:
        await message.answer(
            f"... va yana {len(rows) - 20} ta ro'yxat bor. "
            f"To'liq ro'yxat uchun /export yoki /export_excel buyrug'idan foydalaning."
        )


@router.message(Command("export"))
async def cmd_export(message: Message):
    """SQLite baza faylini (.db) to'g'ridan-to'g'ri yuboradi."""
    if not is_admin(message.from_user.id):
        return
    if not os.path.exists(DB_PATH):
        await message.answer("Baza fayli topilmadi.")
        return
    await message.answer_document(
        FSInputFile(DB_PATH),
        caption=(
            "📦 SQLite baza fayli.\n"
            "Ochish uchun: DB Browser for SQLite (bepul dastur) yoki "
            "VS Code'dagi SQLite kengaytmasidan foydalaning."
        ),
    )


@router.message(Command("export_excel"))
async def cmd_export_excel(message: Message):
    """Bazani Excel (.xlsx) faylga aylantirib yuboradi."""
    if not is_admin(message.from_user.id):
        return

    rows = get_all_registrations()
    if not rows:
        await message.answer("Hozircha hech kim ro'yxatdan o'tmagan.")
        return

    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Ro'yxat"

    headers = [
        "ID", "Ism familiya", "Manzil", "Fan", "Tajriba (yil)",
        "Telefon", "Telegram ID", "Username", "Sana",
    ]
    ws.append(headers)

    for row in rows:
        ws.append([
            row["id"],
            row["full_name"],
            row["region"],
            row["subject"],
            row["experience"],
            row["phone"],
            row["telegram_id"],
            row["username"],
            row["created_at"],
        ])

    # Ustun kengligini avtomatik moslashtirish
    for col_cells in ws.columns:
        max_len = max(len(str(c.value)) if c.value is not None else 0 for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 3, 40)

    export_path = "export_temp.xlsx"
    wb.save(export_path)

    await message.answer_document(
        FSInputFile(export_path, filename="royxatdan_otganlar.xlsx"),
        caption=f"📊 Jami: {len(rows)} ta ro'yxat.",
    )

    os.remove(export_path)
