import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, ConversationHandler, MessageHandler, filters
)

# === BOT MA'LUMOTLARI ===
BOT_TOKEN = "8391288484:AAEKfIE8Ptr6OviApiVa7jaPlxUT6nzjriQ"  # Token
ADMIN_ID = 649076501  # Admin ID

# === LOGGING ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# === MAHSULOTLAR RO‘YXATI (15 ta) ===
PRODUCTS = {
    "qazi": {"name": "Qazi (dona)", "price": 180000, "img": "https://example.com/qazi.jpg"},
    "ot_tarash": {"name": "Qarta qazi (kg)", "price": 60000, "img": "https://example.com/otarash.jpg"},
    "toy_tarash": {"name": "Mol go'shti rulet (kg)", "price": 180000, "img": "https://example.com/toytarash.jpg"},
    "til": {"name": "Til rulet (kg)", "price": 170000, "img": "https://example.com/til.jpg"},
    "mix_rulet": {"name": "Miramir Mix rulet (kg)", "price": 140000, "img": "https://example.com/mix.jpg"},
    "pay_rulet": {"name": "Qoy go'shti rulet (kg)", "price": 195000, "img": "https://example.com/pay.jpg"},
    "indeyka_tovuq": {"name": "Tovuq rulet (kg)", "price": 90000, "img": "https://example.com/tovuq.jpg"},
    "indeyka": {"name": "Indeyka qazi (kg)", "price": 120000, "img": "https://example.com/indeyka.jpg"},
    "kab_kalbasa_yogsiz": {"name": "Kabcho'nniy kalbasa yog'siz (dona)", "price": 75000, "img": "https://example.com/yogsiz.jpg"},
    "kab_kalbasa_yogli": {"name": "Kabcho'nniy kalbasa yog'li (dona)", "price": 60000, "img": "https://example.com/yogli.jpg"},
    "var_kalbasa_yogli": {"name": "Varyonniy kalbasa yog'li (kg)", "price": 95000, "img": "https://example.com/varyogli.jpg"},
    "var_kalbasa_yogsiz": {"name": "Varyonniy kalbasa yog'siz (kg)", "price": 20000, "img": "https://example.com/varyogsiz.jpg"},
    "sasiska_quyon": {"name": "Sasiska quyon (kg)", "price": 115000, "img": "https://example.com/quyon.jpg"},
    "sasiska": {"name": "Sasiska mol (kg)", "price": 90000, "img": "https://example.com/sasiska.jpg"},
    "sosiska_kab": {"name": "Sasiska tovuq (kg)", "price": 70000, "img": "https://example.com/tovuq_sosiska.jpg"},
}

# Savatcha
SAVATCHA = {}
ASK_ADDRESS, ASK_PHONE = range(2)

# === START ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🫶 Assalomu alaykum!\n"
        "Bizning go‘sht va fastfood do‘konimizga xush kelibsiz!\n\n"
        "🍖 /menu - Mahsulotlar\n"
        "🛒 /savatcha - Savatchani ko‘rish"
    )
    await update.message.reply_text(text)

# === MENU ===
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    row = []
    for i, (key, info) in enumerate(PRODUCTS.items(), start=1):
        row.append(InlineKeyboardButton(f"{info['name']} 🛒", callback_data=key))
        if i % 3 == 0:  # har 3 tadan keyin yangi qatordan
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🛒 Savatchani ko‘rish", callback_data="savatcha")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Quyidagi mahsulotlardan tanlang:", reply_markup=reply_markup)

# === MENU CALLBACK ===
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "savatcha":
        await show_savatcha(update, context)
        return

    item = PRODUCTS.get(query.data)
    if not item:
        await query.message.reply_text("Mahsulot topilmadi ❌")
        return

    caption = f"{item['name']}\nNarx: {item['price']} so‘m"
    keyboard = [[InlineKeyboardButton("🛒 Savatchaga qo‘shish", callback_data=f"add_{query.data}")]]
    await query.message.reply_photo(photo=item["img"], caption=caption, reply_markup=InlineKeyboardMarkup(keyboard))

# === SAVATCHAGA QO‘SHISH ===
async def add_to_savatcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    key = query.data.replace("add_", "")
    item = PRODUCTS.get(key)

    if not item:
        await query.message.reply_text("Mahsulot topilmadi ❌")
        return

    SAVATCHA.setdefault(user_id, [])
    SAVATCHA[user_id].append(item)
    await query.message.reply_text(f"✅ {item['name']} savatchaga qo‘shildi!\n/menu yoki /savatcha ni bosing.")

# === SAVATCHA ===
async def show_savatcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    message = query.message if query else update.message
    user_id = update.effective_user.id
    items = SAVATCHA.get(user_id, [])

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
    items = SAVATCHA.get(user.id, [])
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

    # Adminga yuborish
    await context.bot.send_message(chat_id=ADMIN_ID, text=order_text)
    # Foydalanuvchiga javob
    await update.message.reply_text("✅ Buyurtmangiz qabul qilindi!\nAdminimiz siz bilan tez orada bog‘lanadi 😊")

    SAVATCHA[user.id] = []  # Savatchani tozalash
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
    app.add_handler(CommandHandler("savatcha", show_savatcha))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^(?!add_).+"))
    app.add_handler(CallbackQueryHandler(add_to_savatcha, pattern="^add_"))
    app.add_handler(conv_handler)

    print("✅ Bot ishga tushdi. Telegram’da /start yozing.")
    app.run_polling()


if __name__ == "__main__":
    print("✅ Bot ishga tushdi. Telegram’da /start yozing.")
    main()
