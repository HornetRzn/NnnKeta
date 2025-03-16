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
            text="📝 Ответьте на 2 вопроса:\n1. Ваше имя?\n2. Причина вступления (каждое с новой строки)"
        )
        context.user_data['awaiting_answers'] = True
    except Exception as e:
        logging.error(f"Ошибка: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_answers'):
        user = update.message.from_user
        answers = update.message.text.split('\n')
        if len(answers) >= 2:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🚨 Новая заявка!\n👤 Имя: {answers[0]}\n💬 Причина: {answers[1]}\n🆔 ID: {user.id}"
            )
            await update.message.reply_text("✅ Заявка отправлена!")
            context.user_data['awaiting_answers'] = False
        else:
            await update.message.reply_text("❌ Нужно 2 ответа!")

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
