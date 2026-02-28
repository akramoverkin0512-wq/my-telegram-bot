import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- SOZLAMALAR ---
API_TOKEN = "7546274472:AAHT0V9LhK2V6p5Y-7F4_8D9G0H1J2K3L4M" # O'zingizning yangi tokeningizni qo'ying
ADMIN_ID = 5670469794 # Sizning ID raqamingiz

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- KLAVIATURA (ASOSIY MENYU) ---
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
        f"👋 Assalomu alaykum, {message.from_user.full_name}!\n\n"
        "O'z mahallangiz obodonchiligi uchun ovoz yig'ish botiga xush kelibsiz! 🚀\n"
        "Ovoz bering, skrinshot yuboring va sovg'alar yutib oling!",
        reply_markup=main_menu
    )

# --- YORDAM TUGMASI ---
@dp.message(F.text == "🆘 Yordam")
async def help_handler(message: types.Message):
    await message.answer(
        "❓ Savollaringiz bormi? Admin bilan bog'laning:\n\n"
        "👨‍💻 Admin: @Erkin_Akramov",
        reply_markup=main_menu
    )

# --- OVOZ BERISH ---
@dp.message(F.text == "🗳 Ovoz berish")
async def vote_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Loyiha sahifasi 🌐", url="https://openbudget.uz"))
    
    await message.answer(
        "🚀 Ovoz berish bo'yicha yo'riqnoma:\n\n"
        "1️⃣ Pastdagi tugma orqali loyihaga o'ting.\n"
        "2️⃣ Sahifadagi 'Ovoz berish' tugmasini bosing.\n"
        "3️⃣ SMS kodni kiriting.\n"
        "4️⃣ Muvaffaqiyatli ovoz berilgani haqidagi xabarni skrinshot qilib shu botga yuboring!",
        reply_markup=builder.as_markup()
    )

# --- SKRINSHOT QABUL QILISH VA ADMINGA YUBORISH ---
@dp.message(F.photo)
async def photo_handler(message: types.Message):
    await message.answer("📥 **Skrinshot qabul qilindi!**\nAdmin tasdiqlashini kuting...")
    
    # Admin uchun tugmalar
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
            f"ID: {message.from_user.id}\n"
            f"Username: @{message.from_user.username}\n\n"
            f"Tasdiqlaysizmi?"
        ),
        reply_markup=builder.as_markup()
    )

# --- ADMIN TASDIQLASHI ---
@dp.callback_query(F.data.startswith("accept_"))
async def admin_accept(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await bot.send_message(user_id, "🎉 **Tabriklaymiz!**\nSkrinshotingiz tasdiqlandi. Hisobingizga 1 ball qo'shildi!")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n🟢 **TASDIQLANDI**")
    await callback.answer()

@dp.callback_query(F.data.startswith("reject_"))
async def admin_reject(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    await bot.send_message(user_id, "⚠️ **Rad etildi!**\nSkrinshotingiz talabga javob bermaydi. Iltimos, qayta yuboring.")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n🔴 **RAD ETILDI**")
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
