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

# --- MYSQL ULANISHI ---
def get_db():
    return mysql.connector.connect(
        host=os.getenv('MYSQLHOST'),
        user=os.getenv('MYSQLUSER'),
        password=os.getenv('MYSQLPASSWORD'),
        database=os.getenv('MYSQLDATABASE'),
        port=int(os.getenv('MYSQLPORT', 3306))
    )

# --- ASOSIY MENYU ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🗳 Ovoz berish"), KeyboardButton(text="👤 Mening profilim")],
        [KeyboardButton(text="📢 Taklifnoma"), KeyboardButton(text="🏆 Reyting")],
        [KeyboardButton(text="🆘 Yordam")]
    ],
    resize_keyboard=True
)

# --- BUYRUQLAR VA TUGMALAR ---

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT IGNORE INTO users (user_id, full_name) VALUES (%s, %s)", 
                       (message.from_user.id, message.from_user.full_name))
        conn.commit()
        conn.close()
    except: pass
    await message.answer(f"👋 Salom {message.from_user.full_name}! Open Budget botingiz tayyor. Kerakli bo'limni tanlang:", reply_markup=main_menu)

# PROFIL TUGMASI
@dp.message(F.text == "👤 Mening profilim")
async def profile_handler(message: types.Message):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT points, votes FROM users WHERE user_id = %s", (message.from_user.id,))
        res = cursor.fetchone()
        conn.close()
        p, v = res if res else (0, 0)
        await message.answer(f"📋 **Sizning profilingiz:**\n\n👤 Ism: {message.from_user.full_name}\n🌟 Ballar: {p}\n📸 Ovozlar: {v}")
    except:
        await message.answer("⚠️ Profil ma'lumotlarini yuklashda xato yuz berdi.")

# REYTING TUGMASI
@dp.message(F.text == "🏆 Reyting")
async def rating_handler(message: types.Message):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, points FROM users ORDER BY points DESC LIMIT 10")
        users = cursor.fetchall()
        conn.close()
        text = "🏆 **Eng faol foydalanuvchilar:**\n\n"
        for i, (name, p) in enumerate(users, 1):
            text += f"{i}. {name} — {p} ball\n"
        await message.answer(text)
    except:
        await message.answer("⚠️ Reytingni yuklashda xato yuz berdi.")

# YORDAM TUGMASI
@dp.message(F.text == "🆘 Yordam")
async def help_handler(message: types.Message):
    await message.answer("🆘 Savollaringiz bo'lsa, adminga murojaat qiling:\n\n👨‍💻 Admin: @Erkin_Akramov")

# OVOZ BERISH TUGMASI
@dp.message(F.text == "🗳 Ovoz berish")
async def vote_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Saytga o'tish 🌐", url="https://openbudget.uz"))
    await message.answer("🚀 Ovoz bering va tasdiqlovchi skrinshotni shu yerga yuboring!", reply_markup=builder.as_markup())

# TAKLIFNOMA TUGMASI
@dp.message(F.text == "📢 Taklifnoma")
async def invite_handler(message: types.Message):
    bot_info = await bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
    await message.answer(f"🔗 Sizning referal havolangiz:\n{link}\n\nDo'stlarni taklif qiling va ballar to'plang!")

# --- SKRINSHOT QABUL QILISH ---
@dp.message(F.photo)
async def photo_handler(message: types.Message):
    await message.answer("📥 Skrinshot qabul qilindi. Admin tasdiqlashini kuting...")
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"accept_{message.from_user.id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{message.from_user.id}")
    )
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                         caption=f"👤 Foydalanuvchi: {message.from_user.full_name}\nID: {message.from_user.id}",
                         reply_markup=builder.as_markup())

# --- ADMIN QARORI ---
@dp.callback_query(F.data.startswith("accept_"))
async def admin_accept(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET points = points + 1, votes = votes + 1 WHERE user_id = %s", (uid,))
        conn.commit()
        conn.close()
        await bot.send_message(uid, "🎉 Skrinshotingiz tasdiqlandi! Ball qo'shildi.")
        await call.message.edit_caption(caption=call.message.caption + "\n\n🟢 TASDIQLANDI")
    except:
        await call.answer("Bazaga ulanishda xato!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
