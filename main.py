import os
import asyncio
import mysql.connector
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- SIZNING DOIMIY MA'LUMOTLARINGIZ ---
# Tokenni BotFather'dan yangilaganingizdan so'ng shu yerga qo'ying
API_TOKEN = "7546274472:AAHT0V9LhK2V6p5Y-7F4_8D9G0H1J2K3L4M" 
ADMIN_ID = 5670469794 # Sizning admin ID raqamingiz

# --- MYSQL ULANISHI (RAILWAY O'ZGARUVCHILARI ORQALI) ---
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQLHOST'),
        user=os.getenv('MYSQLUSER'),
        password=os.getenv('MYSQL_ROOT_PASSWORD'),
        database=os.getenv('MYSQLDATABASE'),
        port=os.getenv('MYSQLPORT')
    )

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- ASOSIY MENYU (REPLY KEYBOARD) ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🗳 Ovoz berish"), KeyboardButton(text="👤 Mening profilim")],
        [KeyboardButton(text="📢 Taklifnoma"), KeyboardButton(text="🏆 Reyting")],
        [KeyboardButton(text="🆘 Yordam")]
    ],
    resize_keyboard=True
)

# --- START BUYRUG'I ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        f"👋 Assalomu alaykum, {message.from_user.full_name}!\n"
        "Ovoz yig'ish botiga xush kelibsiz! 🚀\n"
        "Ovoz bering va sovg'alar yutib oling!",
        reply_markup=main_menu
    )

# --- YORDAM TUGMASI (@Erkin_Akramov) ---
@dp.message(F.text == "🆘 Yordam")
async def help_handler(message: types.Message):
    await message.answer(
        "❓ Savollaringiz bormi? Admin bilan bog'laning:\n\n"
        "👨‍💻 Admin: @Erkin_Akramov",
        reply_markup=main_menu
    )

# --- OVOZ BERISH VA SKRINSHOT YO'RIQNOMASI ---
@dp.message(F.text == "🗳 Ovoz berish")
async def vote_info(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Loyiha sahifasi 🌐", url="https://openbudget.uz"))
    
    await message.answer(
        "🚀 **Ovoz berish bo'yicha yo'riqnoma:**\n\n"
        "1️⃣ Pastdagi tugma orqali saytga o'ting.\n"
        "2️⃣ Ovoz berib, muvaffaqiyatli xabarni skrinshot qiling.\n"
        "3️⃣ Skrinshotni shu botga yuboring! ✅",
        reply_markup=builder.as_markup()
    )

# --- SKRINSHOTNI QABUL QILISH VA ADMINGA YUBORISH ---
@dp.message(F.photo)
async def photo_handler(message: types.Message):
    await message.answer("📥 **Skrinshot qabul qilindi!**\nAdmin tasdiqlashini kuting...")
    
    # Admin uchun Tasdiqlash/Rad etish tugmalari
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"accept_{message.from_user.id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{message.from_user.id}")
    )
    
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=(
            f"👤 **Yangi skrinshot!**\n"
            f"Ism: {message.from_user.full_name}\n"
            f"ID: {message.from_user.id}\n\n"
            f"Ushbu ovozni tasdiqlaysizmi?"
        ),
        reply_markup=builder.as_markup()
    )

# --- ADMIN QARORI (CALLBACK) ---
@dp.callback_query(F.data.startswith("accept_"))
async def admin_accept(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await bot.send_message(user_id, "🎉 **Tabriklaymiz!**\nOvozingiz tasdiqlandi va 1 ball berildi!")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n🟢 **TASDIQLANDI**")
    await callback.answer("Tasdiqlandi")

@dp.callback_query(F.data.startswith("reject_"))
async def admin_reject(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await bot.send_message(user_id, "⚠️ **Rad etildi!**\nSkrinshot qabul qilinmadi. Qayta yuboring.")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n🔴 **RAD ETILDI**")
    await callback.answer("Rad etildi")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
