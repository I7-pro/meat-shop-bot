from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
import asyncio

# === Sozlamalar ===
BOT_TOKEN = "649076501"  # O'zingizning bot tokeningizni yozing
ADMIN_ID = 7211925485  # Admin Telegram ID

# === Mahsulotlar ro‘yxati ===
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

# Foydalanuvchi savatchasi
user_carts = {}

# === /start komandasi ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    row = []
    for i, (key, product) in enumerate(PRODUCTS.items(), start=1):
        row.append(InlineKeyboardButton(product["name"], callback_data=f"buy_{key}"))
        if i % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🛒 Savatcha", callback_data="cart")])
    await update.message.reply_text("🍖 Mahsulotni tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))

# === Tugmalarni qayta ishlash ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    data = query.data

    if data.startswith("buy_"):
        product_id = data.replace("buy_", "")
        product = PRODUCTS[product_id]
        user_carts.setdefault(user_id, []).append(product)
        await query.message.reply_text(f"✅ {product['name']} savatchaga qo‘shildi.")

    elif data == "cart":
        items = user_carts.get(user_id, [])
        if not items:
            await query.message.reply_text("🛒 Savatchangiz bo‘sh.")
            return
        total = sum(p["price"] for p in items)
        text = "\n".join([f"• {p['name']} — {p['price']} so‘m" for p in items])
        text += f"\n\n💰 Jami: {total} so‘m"
        keyboard = [[InlineKeyboardButton("📦 Buyurtma berish", callback_data="order")]]
        await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "order":
        items = user_carts.get(user_id, [])
        if not items:
            await query.message.reply_text("Savatchangiz bo‘sh 🛒")
            return
        total = sum(p["price"] for p in items)
        order_text = "\n".join([f"• {p['name']} — {p['price']} so‘m" for p in items])
        order_text += f"\n\n💰 Jami: {total} so‘m"

        user = query.from_user
        admin_message = (
            f"📦 *Yangi buyurtma!*\n\n"
            f"👤 Foydalanuvchi: {user.first_name} @{user.username or ''}\n"
            f"☎️ ID: {user.id}\n\n"
            f"{order_text}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, parse_mode="Markdown")
        await query.message.reply_text("✅ Buyurtma qabul qilindi!\nAdmin siz bilan tez orada bog‘lanadi.")
        user_carts[user_id] = []  # savatchani tozalash

# === Botni ishga tushirish ===
def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🤖 Bot ishga tushdi...")
    app.run_polling(stop_signals=None)

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(0))
    except RuntimeError:
        pass
    run_bot()
