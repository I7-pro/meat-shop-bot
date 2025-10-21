from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# === CONFIG ===
TOKEN = "8391288484:AAEKfIE8Ptr6OviApiVa7jaPlxUT6nzjriQ"
ADMIN_CHAT_ID = "649076501"  # O'zingning Telegram ID'ing

# === MAHSULOTLAR RO'YXATI ===
PRODUCTS = {
    "qazi": {"name": "Qazi (dona)", "price": 180000, "img": "https://raw.githubusercontent.com/I7-pro/meat-shop-bot/main/images/qazi.jpg"},
    "go'sht": {"name": "Mol go‘shti (1kg)", "price": 95000, "img": "https://raw.githubusercontent.com/I7-pro/meat-shop-bot/main/images/gosht.jpg"},
    "tovuq": {"name": "Tovuq (1kg)", "price": 55000, "img": "https://raw.githubusercontent.com/I7-pro/meat-shop-bot/main/images/tovuq.jpg"},
    "kolbasa": {"name": "Kolbasa", "price": 28000, "img": "https://raw.githubusercontent.com/I7-pro/meat-shop-bot/main/images/kolbasa.jpg"},
    "sosiska": {"name": "Sosiska", "price": 20000, "img": "https://raw.githubusercontent.com/I7-pro/meat-shop-bot/main/images/sosiska.jpg"},
    "jigar": {"name": "Jigar (1kg)", "price": 35000, "img": "https://raw.githubusercontent.com/I7-pro/meat-shop-bot/main/images/jigar.jpg"},
    "kabob": {"name": "Kabob", "price": 25000, "img": "https://raw.githubusercontent.com/I7-pro/meat-shop-bot/main/images/kabob.jpg"},
    "steak": {"name": "Steyk", "price": 120000, "img": "https://raw.githubusercontent.com/I7-pro/meat-shop-bot/main/images/steak.jpg"},
    "lahm": {"name": "Qo‘y go‘shti (1kg)", "price": 90000, "img": "https://raw.githubusercontent.com/I7-pro/meat-shop-bot/main/images/lahm.jpg"},
    "pitsa": {"name": "Pitsa", "price": 70000, "img": "https://raw.githubusercontent.com/I7-pro/meat-shop-bot/main/images/pitsa.jpg"},
    "burger": {"name": "Burger", "price": 45000, "img": "https://raw.githubusercontent.com/I7-pro/meat-shop-bot/main/images/burger.jpg"},
    "shashlik": {"name": "Shashlik", "price": 40000, "img": "https://raw.githubusercontent.com/I7-pro/meat-shop-bot/main/images/shashlik.jpg"},
    "lag'mon": {"name": "Lag‘mon", "price": 30000, "img": "https://raw.githubusercontent.com/I7-pro/meat-shop-bot/main/images/lagmon.jpg"},
    "somsa": {"name": "Somsa", "price": 15000, "img": "https://raw.githubusercontent.com/I7-pro/meat-shop-bot/main/images/somsa.jpg"},
    "manty": {"name": "Manti", "price": 25000, "img": "https://raw.githubusercontent.com/I7-pro/meat-shop-bot/main/images/manty.jpg"},
}

# === /start komandasi ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton(p["name"], callback_data=key)] for key, p in PRODUCTS.items()]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("🍖 Assalomu alaykum! Mahsulotni tanlang:", reply_markup=reply_markup)

# === Mahsulot tanlanganda ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product = PRODUCTS[query.data]
    caption = f"📦 {product['name']}\n💰 Narxi: {product['price']} so‘m\n\n📲 Buyurtma berish uchun telefon raqamingizni yuboring."
    context.user_data["selected_product"] = query.data

    await query.message.reply_photo(photo=product["img"], caption=caption)

# === Raqam qabul qilish ===
async def phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_key = context.user_data.get("selected_product")
    if not product_key:
        await update.message.reply_text("Avval mahsulotni tanlang /start")
        return

    product = PRODUCTS[product_key]
    phone = update.message.text.strip()
    user = update.message.from_user

    # Admin'ga yuboriladi
    msg = (
        f"📢 Yangi buyurtma!\n\n"
        f"👤 Mijoz: {user.full_name}\n"
        f"📞 Telefon: {phone}\n"
        f"📦 Mahsulot: {product['name']}\n"
        f"💰 Narxi: {product['price']} so‘m"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
    await update.message.reply_text("✅ Buyurtmangiz qabul qilindi! Tez orada bog‘lanamiz.")

# === Botni ishga tushirish ===
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, phone_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
