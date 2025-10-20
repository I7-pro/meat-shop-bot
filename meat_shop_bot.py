import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

# ==== BOT MA'LUMOTLARI ====
BOT_TOKEN = "8391288484:AAEKfIE8Ptr6OviApiVa7jaPlxUT6nzjriQ"   # BotFather token
ADMIN_ID = 7211925485  # Admin ID

# ==== LOGGING ====
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# ==== DO‘KON MAHSULOTLARI ====
PRODUCTS = {
    "mol": {"name": "Mol go‘shti (1 kg)", "price": 450000},
    "qoy": {"name": "Qo‘y go‘shti (1 kg)", "price": 420000},
    "tovuq": {"name": "Tovuq go‘shti (1 kg)", "price": 180000},
}

# Foydalanuvchilar uchun savatcha
CART = {}
ASK_ADDRESS, ASK_PHONE = range(2)

# ==== BOSHLASH KOMANDASI ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🍖 Menyu", callback_data="menu")],
        [InlineKeyboardButton("🛒 Savatcha", callback_data="cart")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🫶 Assalomu alaykum!\nGo‘sht do‘koniga xush kelibsiz.", reply_markup=reply_markup)

# ==== MENYU ====
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(f"{p['name']} - {p['price']} so‘m", callback_data=key)] for key, p in PRODUCTS.items()
    ]
    keyboard.append([InlineKeyboardButton("🛒 Savatchani ko‘rish", callback_data="cart")])
    await query.message.reply_text("Mahsulotni tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))

# ==== MAHSULOT TANLASH ====
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if query.data == "menu":
        await show_menu(update, context)
        return
    if query.data == "cart":
        await show_cart(update, context)
        return
    item = PRODUCTS.get(query.data)
    if item:
        CART.setdefault(user_id, []).append(item)
        await query.message.reply_text(f"✅ {item['name']} savatchaga qo‘shildi.")
    else:
        await query.message.reply_text("Mahsulot topilmadi.")

# ==== SAVATCHA ====
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    items = CART.get(user_id, [])
    if not items:
        await query.message.reply_text("Savatcha bo‘sh.")
        return
    total = sum(i["price"] for i in items)
    text = "\n".join([f"- {i['name']} — {i['price']} so‘m" for i in items])
    text += f"\n\n💰 Jami: {total} so‘m"
    keyboard = [[InlineKeyboardButton("✅ Buyurtma berish", callback_data="checkout")]]
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ==== BUYURTMA ====
async def checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("📍 Manzilingizni kiriting:")
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
        f"👤 {user.first_name} (@{user.username})\n"
        f"📍 {address}\n"
        f"📞 {phone}\n"
        f"💰 {total} so‘m\n\n"
        "🛒 Buyurtma tarkibi:\n"
        + "\n".join(f"- {i['name']} — {i['price']} so‘m" for i in items)
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=order_text)
    await update.message.reply_text("✅ Buyurtma qabul qilindi!")
    CART[user.id] = []
    return ConversationHandler.END

# ==== ASOSIY ====
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
    app.add_handler(CallbackQueryHandler(menu_callback))
    app.add_handler(conv_handler)
    print("✅ Bot ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    main()
