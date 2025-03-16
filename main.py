import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
    ChatJoinRequestHandler,
)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID'))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
PORT = int(os.environ.get('PORT', 10000))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text="📝 Ваше имя?"
        )
        context.user_data['state'] = 'awaiting_name'  # Начало анкеты
    except Exception as e:
        logging.error(f"Ошибка: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    state = user_data.get('state')

    if state == 'awaiting_name':
        user_data['name'] = update.message.text
        user_data['state'] = 'awaiting_age'
        await update.message.reply_text("🔢 Сколько вам лет?")

    elif state == 'awaiting_age':
        if not update.message.text.isdigit():
            await update.message.reply_text("❌ Возраст должен быть числом. Попробуйте еще раз!")
            return
        user_data['age'] = update.message.text
        user_data['state'] = 'awaiting_city'
        await update.message.reply_text("🏙️ Ваш город?")

    elif state == 'awaiting_city':
        user_data['city'] = update.message.text
        user_data['state'] = 'awaiting_reason'
        await update.message.reply_text("💬 Причина вступления?")

    elif state == 'awaiting_reason':
        user_data['reason'] = update.message.text
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"""🚨 Новая заявка!
👤 Имя: {user_data['name']}
🔢 Возраст: {user_data['age']}
🏙️ Город: {user_data['city']}
💬 Причина: {user_data['reason']}
🆔 ID: {update.message.from_user.id}"""
        )
        await update.message.reply_text("✅ Заявка отправлена!")
        # Очищаем данные
        user_data.clear()

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        secret_token=os.environ.get('SECRET_TOKEN', 'DEFAULT')
    )
