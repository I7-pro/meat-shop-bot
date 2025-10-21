import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# === Sozlamalar ===
BOT_TOKEN = "8391288484:AAEKfIE8Ptr6OviApiVa7jaPlxUT6nzjriQ"
ADMIN_ID = 649076501  # Admin Telegram ID

# === Logger (xatolarni terminalga chiqarish) ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# === Mahsulotlar ro‘yxati ===
PRODUCTS = {
    "qazi": {"name": "Qazi (dona)", "price": 180000},
    "ot_tarash": {"name": "Qarta qazi (kg)", "price": 60000},
    "toy_tarash": {"name": "Mol go'shti rulet (kg)", "price": 180000},
    "til": {"name": "Til rulet (kg)", "price": 170000},
    "mix_rulet": {"name": "Miramir Mix rulet (kg)", "price": 140000},
    "pay_rulet": {"name": "Qoy go'shti rulet (kg)", "price": 195000},
    "indeyka_tovuq": {"name": "Tovuq rulet (kg)", "price": 90000},
    "indeyka": {"name": "Indeyka qazi (kg)", "price": 120000},
    "kab_kalbasa_yogsiz": {"name": "Kabcho’n kalbasa yog’siz (dona)", "price": 75000},
    "kab_kalbasa_yogli": {"name": "Kabcho’n kalbasa yog’li (dona)", "price": 60000},
    "var_kalbasa_yogli": {"name": "Varyonniy kalbasa yog’li (kg)", "price": 95000},
    "var_kalbasa_yogsiz": {"name": "Varyonniy kalbasa yog’siz (kg)", "price": 20000},
    "sasiska_quyon": {"name": "Sasiska quyon (kg)", "price": 115000},
    "sasiska": {"name": "Sasiska mol (kg)", "price": 90000},
    "sosiska_kab": {"name": "Sasiska tovuq (kg)", "price": 70000},
}

# === Har bir foydalanuvchining savatchasi ===
cart = {}

# === /start komandasi ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    row = []

    for i, (key, item) in enumerate(PRODUCTS.items(), 1):
        row.append(InlineKeyboardButton(item["name"], callback_data=f"buy_{key}"))
        if i % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🛒 Savatcha", callback_data="cart")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Mahsulotni tanlang:", reply_markup=reply_markup)

# === Tugmalarni qayta ishlash ===
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # 🛍 Mahsulot qo‘shish
    if data.startswith("buy_"):
        product_id = data[4:]
        product = PRODUCTS[product_id]
        cart.setdefault(user_id, []).append(product)
        await query.message.reply_text(f"{product['name']} savatchaga qo‘shildi ✅")

    # 🛒 Savatchani ko‘rish
    elif data == "cart":
        items = cart.get(user_id, [])
        if not items:
            await query.message.reply_text("Savatchangiz bo‘sh 🛒")
            return

        total = sum(p["price"] for p in items)
        text = "\n".join([f"• {p['name']} - {p['price']:,} so‘m" for p in items])
        text += f"\n\n💰 Jami: {total:,} so‘m"

        keyboard = [[InlineKeyboardButton("📦 Buyurtma berish", callback_data="order")]]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # ✅ Buyurtma berish
    elif data == "order":
        items = cart.get(user_id, [])
        if not items:
            await query.message.reply_text("Savatchangiz bo‘sh!")
            return

        total = sum(p["price"] for p in items)
        text = "\n".join([f"{p['name']} - {p['price']:,} so‘m" for p in items])
        text += f"\n\n💰 Jami: {total:,} so‘m"

        # Admin'ga xabar yuborish
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🆕 Yangi buyurtma:\n\n{text}")
        await query.message.reply_text("✅ Buyurtma qabul qilindi!\nAdmin siz bilan tez orada bog‘lanadi.")

        cart[user_id] = []  # Savatchani tozalash

# === Xatoliklarni qayta ishlash (optional, lekin foydali) ===
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(msg="Xatolik yuz berdi:", exc_info=context.error)

# === Asosiy ishga tushirish funksiyasi ===
def main():
    # Botni yaratish
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlerlarni ro‘yxatdan o‘tkazish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Xatoliklarni logga yozish
    application.add_error_handler(error_handler)

    # Botni polling rejimida ishga tushirish
    logging.info("🤖 Bot ishga tushdi... Ctrl + C bosib to‘xtatishingiz mumkin.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

# === Dastur ishga tushirish ===
if __name__ == "__main__":
    main()

