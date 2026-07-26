# ----------------------------------------------------
# ربات فروش پروکسی / VPN - نسخه اولیه (با اطلاع‌رسانی سفارش)
# ----------------------------------------------------

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ⚠️ توکن ربات خودت رو اینجا بذار (همونی که از BotFather گرفتی)
BOT_TOKEN = "8831432109:AAE8Uq0tUyBf2AiKvxUKFbd4s3ZJT0RQAYE"

# آیدی عددی خود شما - وقتی سفارش جدید بیاد، ربات به همین آیدی پیام می‌فرسته
ADMIN_CHAT_ID = 2064026398

# آدرس پروکسی محلی V2rayN
# توی V2rayN برو تو تنظیمات (Settings) -> Basic Settings و ببین "Socks port" چند نوشته
# (معمولاً پیشفرض 10808 هست) - همون عدد رو جای 10808 بذار
PROXY_URL = "socks5h://127.0.0.1:40808"

# ⚠️ شماره کارتی که کاربر باید بهش پول واریز کنه
CARD_NUMBER = "5022291545430785"
CARD_OWNER_NAME = "رضا آذرشین"

# قیمت پلن‌ها (تومان)
PLANS = {
    "1month": {"title": "۱ ماهه", "price": 130000},
    "2month": {"title": "۲ ماهه", "price": 250000},
    "3month": {"title": "۳ ماهه", "price": 350000},
}


# وقتی کاربر دستور /start رو بزنه، این تابع اجرا میشه
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ساخت دکمه برای هر پلن
    keyboard = []
    for plan_id, plan in PLANS.items():
        button_text = f"{plan['title']} - {plan['price']:,} تومان"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=plan_id)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "سلام 👋\nبه ربات فروش Proxy Master خوش اومدی!\nیکی از پلن‌های زیر رو انتخاب کن:",
        reply_markup=reply_markup,
    )


# وقتی کاربر روی یکی از دکمه‌ها کلیک کنه، این تابع اجرا میشه
async def plan_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # به تلگرام میگه که کلیک دریافت شد

    plan_id = query.data
    plan = PLANS[plan_id]
    user = query.from_user

    # پیام راهنما برای پرداخت
    text = (
        f"پلن انتخابی: {plan['title']}\n"
        f"مبلغ: {plan['price']:,} تومان\n\n"
        f"لطفاً مبلغ رو به شماره کارت زیر واریز کن:\n"
        f"💳 {CARD_NUMBER}\n"
        f"به نام: {CARD_OWNER_NAME}\n\n"
        f"بعد از واریز، عکس رسید رو همینجا برام بفرست تا کانفیگت رو براب بسازم و بفرستم."
    )
    await query.edit_message_text(text)

    # ثبت سفارش در یک فایل ساده تا خودمون ببینیم کی چی سفارش داده
    with open("orders.txt", "a", encoding="utf-8") as f:
        f.write(
            f"کاربر: {user.first_name} (@{user.username}) | آیدی عددی: {user.id} | "
            f"پلن: {plan['title']} | مبلغ: {plan['price']}\n"
        )

    # 🔔 ارسال پیام اطلاع‌رسانی به خود شما (ادمین) توی تلگرام
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            f"🔔 سفارش جدید!\n\n"
            f"کاربر: {user.first_name} (@{user.username})\n"
            f"آیدی عددی کاربر: {user.id}\n"
            f"پلن: {plan['title']}\n"
            f"مبلغ: {plan['price']:,} تومان"
        ),
    )


# اجرای اصلی ربات
def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .proxy(PROXY_URL)
        .get_updates_proxy(PROXY_URL)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(plan_selected))

    print("ربات روشن شد و منتظر پیام‌هاست...")
    app.run_polling()


if __name__ == "__main__":
    main()
