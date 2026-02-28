import os
import asyncio
import mysql.connector
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- SIZNING MA'LUMOTLARINGIZ ---
API_TOKEN = "8214317131:AAHuU1PeLF4pgfmzeS3wV1RRoL5NaKWBWBg"
ADMIN_ID = 5670469794

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- MYSQL ULANISHI (XATOSIZ) ---
def get_db():
    return mysql.connector.connect(
        host=os.getenv('MYSQLHOST'),
        user=os.getenv('MYSQLUSER'),
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        database=os.getenv('MYSQLDATABASE'), # Railway'dagi DB nomi
        port=int(os.getenv('MYSQLPORT', 3306))
    )

# Jadvallarni yaratish
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            full_name VARCHAR(255),
            points INT DEFAULT 0,
            votes INT DEFAULT 0,
            invited_by BIGINT DEFAULT NULL
        )
    """)
    conn.commit()
    conn.close()

# --- KLAVIATURALAR ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🗳 Ovoz berish"), KeyboardButton(text="👤 Mening profilim")],
        [KeyboardButton(text="📢 Taklifnoma"), KeyboardButton(text="🏆 Reyting")],
        [KeyboardButton(text="🆘 Yordam")]
    ],
    resize_keyboard=True
)

# --- START ---
@dp.message(Command("start"))
async def start_handler(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    args = command.args
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
    if not cursor.fetchone():
        invited_by = int(args) if args and args.isdigit() else None
        cursor.execute("INSERT INTO users (user_id, full_name, invited_by) VALUES (%s, %s, %s)", 
                       (user_id, full_name, invited_by))
        conn.commit()
    conn.close()
    await message.answer(f"👋 Salom {full_name}! Open Budget botiga xush kelibsiz!", reply_markup=main_menu)

# --- PROFIL ---
@dp.message(F.text == "👤 Mening profilim")
async def profile(message: types.Message):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT points, votes FROM users WHERE user_id = %s", (message.from_user.id,))
    res = cursor.fetchone()
    conn.close()
    points, votes = res if res else (0, 0)
    await message.answer(f"📋 **Profilingiz:**\n\n👤 Ism: {message.from_user.full_name}\n🌟 Ballar: {points}\n📸 Ovozlar: {votes}")

# --- YORDAM ---
@dp.message(F.text == "🆘 Yordam")
async def help_me(message: types.Message):
    await message.answer("🆘 Muammo bormi? Adminga yozing: @Erkin_Akramov")

# --- OVOZ BERISH ---
@dp.message(F.text == "🗳 Ovoz berish")
async def vote(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Loyiha sahifasi 🌐", url="https://openbudget.uz"))
    await message.answer("🚀 Ovoz bering va tasdiqlovchi rasmni botga yuboring!", reply_markup=builder.as_markup())

# --- ADMIN TASDIQLASHI ---
@dp.message(F.photo)
async def admin_check(message: types.Message):
    await message.answer("📥 Qabul qilindi. Admin tasdiqlashini kuting...")
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"yes_{message.from_user.id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"no_{message.from_user.id}")
    )
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                         caption=f"👤 Foydalanuvchi: {message.from_user.full_name}\nID: {message.from_user.id}",
                         reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("yes_"))
async def accept(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET points = points + 1, votes = votes + 1 WHERE user_id = %s", (uid,))
    conn.commit()
    conn.close()
    await bot.send_message(uid, "🎉 Tabriklaymiz! Skrinshotingiz tasdiqlandi!")
    await call.message.edit_caption(caption=call.message.caption + "\n\n🟢 TASDIQLANDI")

@dp.callback_query(F.data.startswith("no_"))
async def reject(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])
    await bot.send_message(uid, "❌ Skrinshot rad etildi. Qayta yuboring.")
    await call.message.edit_caption(caption=call.message.caption + "\n\n🔴 RAD ETILDI")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
