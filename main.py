import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
    ChatJoinRequestHandler,
    ConversationHandler,
)

# Константы
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID'))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
PORT = int(os.environ.get('PORT', 10000))

# Состояния диалога
NAME, REASON = range(2)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text="📝 Введите ваше имя:"
        )
        return NAME  # Переход к состоянию NAME
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        return ConversationHandler.END

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("📝 Теперь укажите причину вступления:")
    return REASON  # Переход к состоянию REASON

async def get_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['reason'] = update.message.text
    user = update.message.from_user
    
    # Отправка данных администратору
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🚨 Новая заявка!\n👤 Имя: {context.user_data['name']}\n💬 Причина: {context.user_data['reason']}\n🆔 ID: {user.id}"
    )
    
    await update.message.reply_text("✅ Заявка отправлена!")
    context.user_data.clear()  # Очистка временных данных
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Диалог прерван.")
    context.user_data.clear()
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Обработчик диалога
    conv_handler = ConversationHandler(
        entry_points=[ChatJoinRequestHandler(handle_join_request)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_reason)]
        },
        fallbacks=[MessageHandler(filters.ALL, cancel)],
        allow_reentry=True
    )
    
    app.add_handler(conv_handler)
    
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        secret_token=os.environ.get('SECRET_TOKEN', 'DEFAULT')
    )
