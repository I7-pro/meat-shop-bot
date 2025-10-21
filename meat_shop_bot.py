from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request
import logging
import os

# === Sozlamalar ===
BOT_TOKEN = "8391288484:AAEKfIE8Ptr6OviApiVa7jaPlxUT6nzjriQ"
ADMIN_ID = 649076501  # admin Telegram ID
WEBHOOK_URL = "https://meatshopbot.onrender.com"  # o'zingizning Render link'ingiz

# Flask ilovasi
app = Flask(__name__)

# Telegram Application
application = Application.builder().token(BOT_TOKEN).build()

# === Mahsulotlar ro'yxati (sizning variant) ===
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

# Har bir foydalanuvchining savatchasi
cart = {}

# === Start komandasi ===
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

    if data.startswith("buy_"):
        product_id = data[4:]
        product = PRODUCTS[product_id]
        cart.setdefault(user_id, []).append(product)
        await query.message.reply_text(f"{product['name']} savatchaga qo‘shildi ✅")

    elif data == "cart":
        items = cart.get(user_id, [])
        if not items:
            await query.message.reply_text("Savatchangiz bo‘sh 🛒")
            return
        total = sum(p["price"] for p in items)
        text = "\n".join([f"• {p['name']} - {p['price']} so'm" for p in items])
        text += f"\n\nJami: {total} so'm"
        keyboard = [[InlineKeyboardButton("📦 Buyurtma berish", callback_data="order")]]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "order":
        items = cart.get(user_id, [])
        total = sum(p["price"] for p in items)
        text = "\n".join([f"{p['name']} - {p['price']} so'm" for p in items])
        text += f"\n\nJami: {total} so'm"
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🆕 Yangi buyurtma!\n\n{text}")
        await query.message.reply_text("✅ Buyurtma qabul qilindi!\nAdmin siz bilan tez orada bog‘lanadi.")
        cart[user_id] = []

# === Handlerlarni qo‘shish ===
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))

# === Flask webhook ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

@app.route("/")
def index():
    return "Bot is running!"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )
