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

# --- BAZA BILAN BOG'LANISH FUNKSIYASI ---
def get_db():
    return mysql.connector.connect(
        host=os.getenv('MYSQLHOST'),
        user=os.getenv('MYSQLUSER'),
        password=os.getenv('MYSQLPASSWORD'),
        database=os.getenv('MYSQLDATABASE'),
        port=int(os.getenv('MYSQLPORT', 3306))
    )

# Jadvallarni majburiy yaratish
def check_db():
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
        print("✅ Baza va jadvallar tayyor!")
    except Exception as e:
        print(f"❌ Baza xatosi: {e}")

# --- TUGMALAR (TEXTLARNI TO'G'RI YOZING) ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🗳 Ovoz berish"), KeyboardButton(text="👤 Mening profilim")],
        [KeyboardButton(text="📢 Taklifnoma"), KeyboardButton(text="🏆 Reyting")],
        [KeyboardButton(text="🆘 Yordam")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT IGNORE INTO users (user_id, full_name) VALUES (%s, %s)", 
                       (message.from_user.id, message.from_user.full_name))
        conn.commit()
        conn.close()
    except: pass
    await message.answer(f"👋 Salom {message.from_user.full_name}!", reply_markup=main_menu)

# --- TUGMALARNI ISHLATISH (XATOSIZ) ---

@dp.message(F.text == "👤 Mening profilim")
async def profile_btn(message: types.Message):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT points, votes FROM users WHERE user_id = %s", (message.from_user.id,))
        res = cursor.fetchone()
        conn.close()
        p, v = res if res else (0, 0)
        await message.answer(f"📋 **Profilingiz:**\n\n👤 Ism: {message.from_user.full_name}\n🌟 Ballar: {p}\n📸 Ovozlar: {v}")
    except Exception as e:
        await message.answer("⚠️ Ma'lumot topilmadi. Avval /start bosing.")

@dp.message(F.text == "🏆 Reyting")
async def rating_btn(message: types.Message):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, points FROM users ORDER BY points DESC LIMIT 10")
        users = cursor.fetchall()
        conn.close()
        text = "🏆 **TOP 10 foydalanuvchilar:**\n\n"
        for i, (name, p) in enumerate(users, 1):
            text += f"{i}. {name} — {p} ball\n"
        await message.answer(text)
    except:
        await message.answer("⚠️ Reyting vaqtinchalik ishlamayapti.")

@dp.message(F.text == "🆘 Yordam")
async def help_btn(message: types.Message):
    await message.answer("🆘 Savollar uchun admin: @Erkin_Akramov")

@dp.message(F.photo)
async def photo_handler(message: types.Message):
    await message.answer("📥 Skrinshot qabul qilindi. Admin tasdiqlashini kuting...")
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"ok_{message.from_user.id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"no_{message.from_user.id}")
    )
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                         caption=f"Foydalanuvchi: {message.from_user.full_name}\nID: {message.from_user.id}",
                         reply_markup=builder.as_markup())

# --- ADMIN QARORLARI ---

@dp.callback_query(F.data.startswith("ok_"))
async def admin_ok(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE
