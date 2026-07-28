# ----------------------------------------------------
# نسخه یا سئخیندی پلن‌ها / VPN - ریلف فروش پروکسی
# ----------------------------------------------------

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ⚠️ توکن ربات خودت رو اینجا بذار (از BotFather گرفتی)
BOT_TOKEN = "8831432109:AAE8Uq0tUyBf2AiKvxUKFbd4s3ZJT0RQAYE"

# ⚠️ آیدی عددی خودت (ادمین) - سفارش‌های جدید به این آیدی فرستاده میشه
ADMIN_CHAT_ID = 2064026398

# شماره کارتی که کاربر باید بهش پول واریز کنه
CARD_NUMBER = "5022291545430785"
CARD_OWNER_NAME = "رضا آذرشین"

# دسته‌بندی پلن‌ها
CATEGORIES = {
    "fixed": "آیپی ثابت (مخصوص حجمی)",
    "unlimited": "نامحدود (معمولی)",
}

# پلن‌های هر دسته
PLANS = {
    "fixed": {
        "fixed_30g": {"title": "آیپی ثابت ۱ ماهه ۳۰ گیگ تک کاربره", "price": 400000},
        "fixed_20g": {"title": "آیپی ثابت ۱ ماهه ۲۰ گیگ تک کاربره", "price": 300000},
        "fixed_10g": {"title": "آیپی ثابت ۱ ماهه ۱۰ گیگ تک کاربره", "price": 200000},
    },
    "unlimited": {
        "unl_1m": {"title": "نامحدود ۱ ماهه", "price": 130000},
        "unl_2m": {"title": "نامحدود ۲ ماهه", "price": 250000},
        "unl_3m": {"title": "نامحدود ۳ ماهه", "price": 350000},
    },
}


def build_category_keyboard():
    keyboard = []
    for cat_id, title in CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(title, callback_data=f"cat:{cat_id}")])
    return InlineKeyboardMarkup(keyboard)


def build_plans_keyboard(cat_id):
    keyboard = []
    for plan_id, plan in PLANS[cat_id].items():
        button_text = f"{plan['title']} - {plan['price']:,} تومان"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"plan:{plan_id}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back:categories")])
    return InlineKeyboardMarkup(keyboard)


# وقتی کاربر دستور /start رو بزنه
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\nبه ربات فروش Proxy Master خوش اومدی!\nپلن VPN خود را انتخاب کنید:",
        reply_markup=build_category_keyboard(),
    )


# مدیریت همه‌ی کلیک‌های دکمه (دسته، پلن، بازگشت)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # کاربر یک دسته (آیپی ثابت / نامحدود) رو انتخاب کرده
    if data.startswith("cat:"):
        cat_id = data.split(":", 1)[1]
        await query.edit_message_text(
            f"{CATEGORIES[cat_id]}\nیکی از پلن‌های زیر رو انتخاب کن:",
            reply_markup=build_plans_keyboard(cat_id),
        )
        return

    # کاربر دکمه بازگشت رو زده -> برگرد به انتخاب دسته
    if data == "back:categories":
        await query.edit_message_text(
            "پلن VPN خود را انتخاب کنید:",
            reply_markup=build_category_keyboard(),
        )
        return

    # کاربر یک پلن نهایی رو انتخاب کرده
    if data.startswith("plan:"):
        plan_id = data.split(":", 1)[1]
        plan = None
        for cat_plans in PLANS.values():
            if plan_id in cat_plans:
                plan = cat_plans[plan_id]
                break

        user = query.from_user
        text = (
            f"پلن انتخابی: {plan['title']}\n"
            f"مبلغ: {plan['price']:,} تومان\n\n"
            f"لطفاً مبلغ رو به شماره کارت زیر واریز کن:\n"
            f"💳 {CARD_NUMBER}\n"
            f"به نام: {CARD_OWNER_NAME}\n\n"
            f"بعد از واریز، عکس رسید رو همینجا برام بفرست تا کانفیگت رو براب بسازم و بفرستم."
        )
        await query.edit_message_text(text)

        # ثبت سفارش در فایل
        with open("orders.txt", "a", encoding="utf-8") as f:
            f.write(
                f"کاربر: {user.first_name} (@{user.username}) | آیدی عددی: {user.id} | "
                f"پلن: {plan['title']} | مبلغ: {plan['price']}\n"
            )

        # 🔔 اطلاع‌رسانی سفارش جدید به ادمین (خودت) توی تلگرام
        admin_text = (
            "🔔 سفارش جدید!\n\n"
            f"کاربر: {user.first_name} (@{user.username})\n"
            f"آیدی عددی کاربر: {user.id}\n"
            f"پلن: {plan['title']}\n"
            f"مبلغ: {plan['price']:,} تومان"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text)
        return


# دستور ادمین برای ارسال کانفیگ به مشتری: /send USER_ID config_text
async def send_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # فقط خود ادمین بتونه از این دستور استفاده کنه
    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text("فرمت درست: /send USER_ID config_text")
        return

    target_user_id = context.args[0]
    config_text = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=int(target_user_id), text=config_text)
        await update.message.reply_text("✅ کانفیگ با موفقیت برای مشتری ارسال شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ ارسال ناموفق بود: {e}")


def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_config))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("ربات روشن شد و منتظر پیام‌هاست...")
    app.run_polling()


if __name__ == "__main__":
    main()
