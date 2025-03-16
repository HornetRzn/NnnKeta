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
        context.user_data['state'] = 'awaiting_name'  # Устанавливаем состояние
    except Exception as e:
        logging.error(f"Ошибка: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    state = user_data.get('state')

    if state == 'awaiting_name':
        # Сохраняем имя и запрашиваем причину
        user_data['name'] = update.message.text
        user_data['state'] = 'awaiting_reason'
        await update.message.reply_text("💬 Причина вступления?")
    
    elif state == 'awaiting_reason':
        # Сохраняем причину и отправляем заявку
        user_data['reason'] = update.message.text
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🚨 Новая заявка!\n👤 Имя: {user_data['name']}\n💬 Причина: {user_data['reason']}\n🆔 ID: {update.message.from_user.id}"
        )
        await update.message.reply_text("✅ Заявка отправлена!")
        # Очищаем данные
        user_data.pop('state', None)
        user_data.pop('name', None)
        user_data.pop('reason', None)

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
