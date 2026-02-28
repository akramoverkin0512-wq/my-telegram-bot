import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Sizning ma'lumotlaringiz
API_TOKEN = "7546274472:AAHT0V9LhK2V6p5Y-7F4_8D9G0H1J2K3L4M" # BotFather'dan olgan yangi tokeningizni shu yerga qo'ying
ADMIN_ID = 5670469794 # Sizning ID raqamingiz

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- FOYDALANUVCHI UCHUN ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 **Salom! Open Budget rasmiy yordamchisiga xush kelibsiz.**\n\n"
        "Ovoz berganingizni tasdiqlash uchun skrinshotni shu yerga yuboring. ✅"
    )

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("✅ **Skrinshot qabul qilindi.**\nAdmin tasdiqlashini kuting...")
    
    # Adminga yuborish tugmalari (Tasdiqlash/Rad etish)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"accept_{message.from_user.id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{message.from_user.id}")
    )
    
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=(
            f"👤 **Yangi skrinshot!**\n\n"
            f"Ism: {message.from_user.full_name}\n"
            f"ID: {message.from_user.id}\n\n"
            f"Ushbu foydalanuvchini tasdiqlaysizmi?"
        ),
        reply_markup=builder.as_markup()
    )

# --- ADMIN UCHUN ---
@dp.callback_query(F.data.startswith("accept_"))
async def accept_user(callback: types.Callback_query):
    user_id = int(callback.data.split("_")[1])
    await bot.send_message(user_id, "🎉 **Tabriklaymiz!**\nSizning ovozingiz tasdiqlandi va ball berildi.")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n🟢 **TASDIQLANDI**")
    await callback.answer("Tasdiqlandi!")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_user(callback: types.Callback_query):
    user_id = int(callback.data.split("_")[1])
    await bot.send_message(user_id, "⚠️ **Uzr!**\nSiz yuborgan skrinshot rad etildi. Iltimos, qayta yuboring.")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n🔴 **RAD ETILDI**")
    await callback.answer("Rad etildi!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
