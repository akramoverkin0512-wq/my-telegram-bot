import os
import asyncio
import mysql.connector
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- DOIMIY MA'LUMOTLAR ---
API_TOKEN = "8214317131:AAHuU1PeLF4pgfmzeS3wV1RRoL5NaKWBWBg"
ADMIN_ID = 5670469794

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- MYSQL ULANISHI (XATOSIZ VERSIYA) ---
def get_db():
    # Railway o'zgaruvchilarini tekshirish
    host = os.getenv('MYSQLHOST')
    user = os.getenv('MYSQLUSER')
    password = os.getenv('MYSQLPASSWORD')
    port = int(os.getenv('MYSQLPORT', 3306))
    database = os.getenv('MYSQLDATABASE') # AGAR BU BO'SH BO'LSA XATO BERADI

    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=database
    )

# Jadvallarni yaratish
def init_db():
    try:
        conn = get_db()
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
        print("✅ Baza muvaffaqiyatli ulandi va jadval yaratildi!")
    except Exception as e:
        print(f"❌ Baza bilan bog'lanishda xato: {e}")

# --- TUGMALAR ---
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
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT IGNORE INTO users (user_id, full_name) VALUES (%s, %s)", 
                       (message.from_user.id, message.from_user.full_name))
        conn.commit()
        conn.close()
    except:
        pass
    
    await message.answer(f"👋 Salom {message.from_user.full_name}!\nBot ishga tushdi!", reply_markup=main_menu)

# --- YORDAM TUGMASI ---
@dp.message(F.text == "🆘 Yordam")
async def help_handler(message: types.Message):
    await message.answer("❓ Savollaringiz bo'lsa adminga yozing:\n\n👨‍💻 Admin: @Erkin_Akramov")

# --- ADMIN TASDIQLASHI ---
@dp.message(F.photo)
async def photo_handler(message: types.Message):
    await message.answer("📥 Skrinshot qabul qilindi. Admin tasdiqlashini kuting...")
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"ok_{message.from_user.id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"no_{message.from_user.id}")
    )
    
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=f"👤 Foydalanuvchi: {message.from_user.full_name}\nID: {message.from_user.id}",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data.startswith("ok_"))
async def accept_vote(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET points = points + 1, votes = votes + 1 WHERE user_id = %s", (user_id,))
        conn.commit()
        conn.close()
        await bot.send_message(user_id, "🎉 Tabriklaymiz! Skrinshotingiz tasdiqlandi!")
    except:
        await callback.answer("Baza bilan muammo!")
    
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n🟢 TASDIQLANDI")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
