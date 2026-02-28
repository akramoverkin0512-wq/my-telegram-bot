import asyncio
import mysql.connector
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

# .env faylidan yuklash
load_dotenv()

logging.basicConfig(level=logging.INFO)

# O'zgaruvchilar
API_TOKEN = os.getenv('8601504386:AAFGATm2hhy_ZYTn04WMvAN2--3b2RV4DmI')
ADMIN_ID = int(os.getenv('ADMIN_ID', '5670469794'))

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQLHOST'),
        user=os.getenv('MYSQLUSER'),
        password=os.getenv('MYSQLPASSWORD'),
        database=os.getenv('MYSQLDATABASE'),
        port=os.getenv('MYSQLPORT')
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY, 
            full_name VARCHAR(255),
            points INT DEFAULT 0
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- HANDLERS ---

@dp.message(CommandStart())
async def start(message: types.Message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, full_name) 
        VALUES (%s, %s) 
        ON DUPLICATE KEY UPDATE full_name = %s
    """, (message.from_user.id, message.from_user.full_name, message.from_user.full_name))
    conn.commit()
    cursor.close()
    conn.close()
    
    await message.answer(f"👋 Salom, {message.from_user.full_name}!\nOvoz bering va skrinshot yuboring.\n\n🏆 /top - Reytingni ko'rish")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.reply("✅ Qabul qilindi! Admin tasdiqlashini kuting.")
    
    kb = InlineKeyboardBuilder()
    kb.button(text="Tasdiqlash ✅", callback_data=f"ok_{message.from_user.id}")
    kb.button(text="Rad etish ❌", callback_data=f"no_{message.from_user.id}")
    kb.adjust(2)
    
    await bot.send_photo(
        chat_id=ADMIN_ID, 
        photo=message.photo[-1].file_id, 
        caption=f"👤 Kimdan: {message.from_user.full_name}\n🆔 ID: {message.from_user.id}",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data.startswith("ok_"))
async def approve(callback: types.CallbackQuery):
    uid = int(callback.data.split("_")[1])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET points = points + 1 WHERE user_id = %s", (uid,))
    conn.commit()
    cursor.close()
    conn.close()
    
    await bot.send_message(uid, "🎉 Tabriklaymiz! Skrinshotingiz tasdiqlandi va 1 ball berildi.")
    await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n✅ STATUS: TASDIQLANDI")
    await callback.answer("Tasdiqlandi")

@dp.callback_query(F.data.startswith("no_"))
async def reject(callback: types.CallbackQuery):
    uid = int(callback.data.split("_")[1])
    await bot.send_message(uid, "❌ Afsuski, skrinshotingiz rad etildi.")
    await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n❌ STATUS: RAD ETILDI")
    await callback.answer("Rad etildi")

@dp.message(Command("top"))
async def show_top(message: types.Message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, points FROM users ORDER BY points DESC LIMIT 50")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        await message.answer("Ro'yxat bo'sh.")
        return

    text = "🏆 **TOP-50 REYTING:**\n\n"
    for i, (name, p) in enumerate(rows, 1):
        text += f"{i}. {name} — {p} ball\n"
    
    await message.answer(text)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())