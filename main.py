import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
    ChatJoinRequestHandler,
    CommandHandler,
    ConversationHandler,
)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID'))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
PORT = int(os.environ.get('PORT', 10000))

# Этапы анкетирования
QUESTION_1, QUESTION_2, QUESTION_3, QUESTION_4, QUESTION_5 = range(5)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    try:
        # Сохраняем ID пользователя для дальнейшего общения
        context.user_data['user_id'] = user.id
        # Отправляем первый вопрос
        await context.bot.send_message(
            chat_id=user.id,
            text="Привет! Ответьте на вопросы для вступления:\n**1. Как вас зовут?**"
        )
        return QUESTION_1
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        return ConversationHandler.END

async def handle_answer_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        return  # Игнорируем сообщения не из личного чата
    context.user_data["question_1"] = update.message.text
    await update.message.reply_text("**2. Какие навыки у вас есть?**")
    return QUESTION_2

async def handle_answer_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question_2"] = update.message.text
    await update.message.reply_text("**3. Почему вы хотите вступить?**")
    return QUESTION_3

async def handle_answer_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question_3"] = update.message.text
    await update.message.reply_text("**4. Как вы узнали о нас?**")
    return QUESTION_4

async def handle_answer_4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question_4"] = update.message.text
    await update.message.reply_text("**5. Ваше сообщение админу?**")
    return QUESTION_5

async def handle_answer_5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question_5"] = update.message.text
    user_id = context.user_data['user_id']
    
    # Формируем отчет для админа
    report = (
        f"🚨 **Новая заявка!**\n"
        f"🆔 ID: `{user_id}`\n"
        f"📝 Ответы:\n"
        f"1. {context.user_data['question_1']}\n"
        f"2. {context.user_data['question_2']}\n"
        f"3. {context.user_data['question_3']}\n"
        f"4. {context.user_data['question_4']}\n"
        f"5. {context.user_data['question_5']}"
    )
    
    await context.bot.send_message(chat_id=ADMIN_ID, text=report)
    await update.message.reply_text("✅ Заявка отправлена!")
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Анкета отменена.")
    context.user_data.clear()
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Настройка ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[ChatJoinRequestHandler(handle_join_request)],
        states={
            QUESTION_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer_1)],
            QUESTION_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer_2)],
            QUESTION_3: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer_3)],
            QUESTION_4: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer_4)],
            QUESTION_5: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer_5)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    app.add_handler(conv_handler)
    
    # Вебхук
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        secret_token=os.environ.get('SECRET_TOKEN', 'DEFAULT')
    )
