import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

# === BOT MA'LUMOTLARI ===
BOT_TOKEN = "8391288484:AAEKfIE8Ptr6OviApiVa7jaPlxUT6nzjriQ"  # BotFather'dan olingan token
ADMIN_ID = 7211925485  # O'zingning Telegram ID'ingni yoz

# === LOGGING ===
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# === MAHSULOTLAR RO‘YXATI (15 ta) ===
PRODUCTS = {
    "qazi": {"name": "Qazi (dona)", "price": 180000, "img": "C:\Users\islom\Desktop\tg bot\photo_2025-10-21_19-16-59.jpg"},
    "ot tarash": {"name": "Qarta qazi (kg)", "price": 60000, "img": "C:\Users\islom\Desktop\tg bot\photo_2025-10-21_19-17-14.jpg"},
    "toy tarash": {"name": "Mol go'shti rulet (kg)", "price": 180000, "img": "C:\Users\islom\Desktop\tg bot\photo_2025-10-21_19-16-33.jpg"},
    "til": {"name": "Til rulet (kg)", "price": 170000, "img": "C:\Users\islom\Desktop\tg bot\photo_2025-10-21_19-49-31.jpg"},
    "mix rulet": {"name": "Miramir Mix rulet (kg)", "price": 140000, "img": "C:\Users\islom\Desktop\tg bot\photo_2025-10-21_19-09-59.jpg"},
    "pay rulet": {"name": "Qoy go'shti rulet (kg)", "price": 195000, "img": "C:\Users\islom\Desktop\tg bot\photo_2025-10-21_19-16-36.jpg"},
    "indeyka tovuq": {"name": "Tovuq rulet (kg)", "price": 90000, "img": "C:\Users\islom\Desktop\tg bot\photo_2025-10-21_19-16-41.jpg"},
    "indeyka": {"name": "Indeyka qazi (kg)", "price": 120000, "img": "C:\Users\islom\Desktop\tg bot\photo_2025-10-21_19-16-38.jpg"},
    "kab kalbasa yog'siz": {"name": "Kabcho'nniy kalbasa yog'li (dona)", "price": 75000, "img": "C:\Users\islom\Desktop\tg bot\photo_2025-10-21_19-16-44.jpg"},
    "kab kalbasa yog'li": {"name": "Kabcho'nniy kalbasa domashniy (dona)", "price": 60000, "img": "C:\Users\islom\Desktop\tg bot\photo_2025-10-21_19-17-01.jpg"},
    "var kalbasa yog'li": {"name": "Varyonniy kalbasa domashniy (kg)", "price": 95000, "img": "C:\Users\islom\Desktop\tg bot\photo_2025-10-21_19-55-07.jpg"},
    "var kalbasa yog'siz": {"name": "Varyonniy kalbasa yog'siz (domashniy)", "price": 20000, "img": ""},
    "sasiska quyon": {"name": "Sasiska quyon (kg)", "price": 115000, "C:\Users\islom\Desktop\tg bot\photo_2025-10-21_19-17-04.jpg"},
    "sasiska": {"name": "Sasiska mol (kg)", "price": 90000, "img": "C:\Users\islom\Desktop\tg bot\photo_2025-10-21_19-17-06.jpg"},
    "sosiska kab": {"name": "Sasiska tovuq (kg)", "price": 70000, "img": "C:\Users\islom\Desktop\tg bot\photo_2025-10-21_19-17-08.jpg"},
    
}

# Savatcha
CART = {}

# Holatlar
ASK_ADDRESS, ASK_PHONE = range(2)


# === START ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🫶 Assalomu alaykum!\n"
        "Bizning go‘sht va fastfood do‘konimizga xush kelibsiz!\n\n"
        "🍖 /menu - Mahsulotlar\n"
        "🛒 /cart - Savatchani ko‘rish"
    )
    await update.message.reply_text(text)


# === MENU ===
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for key, info in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(f"{info['name']} — {info['price']} so‘m", callback_data=key)])
    keyboard.append([InlineKeyboardButton("🛒 Savatchani ko‘rish", callback_data="cart")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Quyidagi mahsulotlardan tanlang:", reply_markup=reply_markup)


# === MENU CALLBACK ===
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "cart":
        await show_cart(update, context)
        return

    item = PRODUCTS.get(query.data)
    if not item:
        await query.message.reply_text("Mahsulot topilmadi ❌")
        return

    # Rasm bilan mahsulotni yuborish
    photo = item["img"]
    caption = f"{item['name']}\nNarx: {item['price']} so‘m"
    keyboard = [[InlineKeyboardButton("🛒 Savatchaga qo‘shish", callback_data=f"add_{query.data}")]]
    await query.message.reply_photo(photo=photo, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard))


# === SAVATCHAGA QO‘SHISH ===
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    key = query.data.replace("add_", "")
    item = PRODUCTS.get(key)
    if not item:
        await query.message.reply_text("Mahsulot topilmadi ❌")
        return

    CART.setdefault(user_id, [])
    CART[user_id].append(item)
    await query.message.reply_text(f"✅ {item['name']} savatchaga qo‘shildi!\n/menu yoki /cart ni bosing.")


# === SAVATCHA ===
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    message = query.message if query else update.message
    user_id = update.effective_user.id
    items = CART.get(user_id, [])

    if not items:
        await message.reply_text("🛒 Savatchangiz hozircha bo‘sh. /menu orqali mahsulot tanlang.")
        return

    total = sum(i["price"] for i in items)
    text = "\n".join([f"- {i['name']} — {i['price']} so‘m" for i in items])
    text += f"\n\n💰 Jami: {total} so‘m"

    keyboard = [[InlineKeyboardButton("✅ Buyurtma berish", callback_data="checkout")]]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# === BUYURTMA ===
async def checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("📍 Iltimos, manzilingizni kiriting:")
    return ASK_ADDRESS


async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    return ASK_PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    phone = update.message.text
    address = context.user_data["address"]
    items = CART.get(user.id, [])
    total = sum(i["price"] for i in items)

    order_text = (
        f"🆕 Yangi buyurtma!\n\n"
        f"👤 Foydalanuvchi: {user.first_name} (@{user.username})\n"
        f"📍 Manzil: {address}\n"
        f"📞 Telefon: {phone}\n"
        f"💰 Jami: {total} so‘m\n\n"
        "🛒 Buyurtma tarkibi:\n"
    )
    for i in items:
        order_text += f"- {i['name']} — {i['price']} so‘m\n"

    # Adminga yuboriladi
    await context.bot.send_message(chat_id=ADMIN_ID, text=order_text)

    # Foydalanuvchiga javob
    await update.message.reply_text("✅ Buyurtmangiz qabul qilindi! Tez orada siz bilan bog‘lanamiz.")
    CART[user.id] = []  # savatchani tozalash
    return ConversationHandler.END


# === ASOSIY QISM ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(checkout_callback, pattern="^checkout$")],
        states={
            ASK_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("cart", show_cart))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^(?!add_).+"))
    app.add_handler(CallbackQueryHandler(add_to_cart, pattern="^add_"))
    app.add_handler(conv_handler)

    print("✅ Bot ishga tushdi. Telegram’da /start yozing.")
    app.run_polling()


if __name__ == "__main__":
    main()
