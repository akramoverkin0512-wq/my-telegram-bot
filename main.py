import os
import asyncio
import mysql.connector
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- SOZLAMALAR ---
API_TOKEN = "8214317131:AAHuU1PeLF4pgfmzeS3wV1RRoL5NaKWBWBg"
ADMIN_ID = 5670469794

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- MYSQL ULANISHI (XATOSIZ) ---
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQLHOST'),
        user=os.getenv('MYSQLUSER'),
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        database=os.getenv('MYSQLDATABASE'), # Shuni topolmayotgan edi
        port=os.getenv('MYSQLPORT')
    )

# Jadvalni yaratish (bot birinchi marta yonganda)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            full_name VARCHAR(255),
            points INT DEFAULT 0,
            votes INT DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# --- KLAVIATURA ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🗳 Ovoz berish"), KeyboardButton(text="👤 Mening profilim")],
        [KeyboardButton(text="📢 Taklifnoma"), KeyboardButton(text="🏆 Reyting")],
        [KeyboardButton(text="🆘 Yordam")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT IGNORE INTO users (user_id, full_name) VALUES (%s, %s)", 
                   (message.from_user.id, message.from_user.full_name))
    conn.commit()
    conn.close()
    
    await message.answer(
        f"👋 Assalomu alaykum, {message.from_user.full_name}!\n"
        "O'z mahallangiz rivojiga hissa qo'shing va sovg'alar yutib oling! 🚀",
        reply_markup=main_menu
    )

@dp.message(F.text == "🆘 Yordam")
async def help_handler(message: types.Message):
    await message.answer("❓ Muammo bo'yicha adminga murojaat qiling: @Erkin_Akramov")

@dp.message(F.text == "👤 Mening profilim")
async def profile_handler(message: types.Message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT points, votes FROM users WHERE user_id = %s", (message.from_user.id,))
    data = cursor.fetchone()
    conn.close()
    
    await message.answer(
        f"📋 **Sizning profilingiz:**\n\n"
        f"👤 Ism: {message.from_user.full_name}\n"
        f"🆔 ID: {message.from_user.id}\n"
        f"🌟 Jami ballar: {data[0] if data else 0}\n"
        f"📸 Tasdiqlangan ovozlar: {data[1] if data else 0}"
    )

@dp.message(F.text == "🗳 Ovoz berish")
async def vote_info(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Loyiha sahifasi 🌐", url="https://openbudget.uz"))
    await message.answer(
        "🚀 **Ovoz bering va skrinshot yuboring!**\n\n"
        "Ovoz bergach, tasdiqlovchi rasmni shu yerga yuboring. ✅",
        reply_markup=builder.as_markup()
    )

# --- ADMIN TASDIQLASHI ---
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("✅ Skrinshot qabul qilindi. Admin tasdiqlashini kuting...")
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"accept_{message.from_user.id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{message.from_user.id}")
    )
    
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=f"👤 **Yangi ovoz!**\nID: {message.from_user.id}\nIsm: {message.from_user.full_name}",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data.startswith("accept_"))
async def accept_vote(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET points = points + 1, votes = votes + 1 WHERE user_id = %s", (user_id,))
    conn.commit()
    conn.close()
    
    await bot.send_message(user_id, "🎉 **Tabriklaymiz!** Skrinshotingiz tasdiqlandi va ball berildi!")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n🟢 **TASDIQLANDI**")
    await callback.answer()

@dp.callback_query(F.data.startswith("reject_"))
async def reject_vote(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await bot.send_message(user_id, "⚠️ **Uzr!** Skrinshotingiz rad etildi.")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n🔴 **RAD ETILDI**")
    await callback.answer()

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
