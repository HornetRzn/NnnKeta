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

# Настройки
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID'))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
PORT = int(os.environ.get('PORT', 10000))

# Этапы анкетирования
QUESTION_1, QUESTION_2, QUESTION_3, QUESTION_4, QUESTION_5 = range(5)

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Функция для отправки вопросов
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, question_text: str, next_state: int):
    await update.message.reply_text(question_text)
    return next_state

# Обработчик запроса вступления в чат
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    try:
        # Начало анкеты
        await context.bot.send_message(
            chat_id=user.id,
            text="Привет! Ответьте на вопросы для вступления:"
        )
        await context.bot.send_message(
            chat_id=user.id,
            text="Вопрос 1: Как вас зовут?"
        )
        context.user_data['user_id'] = user.id
        context.user_data['username'] = user.username or "Нет username"
        context.user_data['full_name'] = f"{user.first_name} {user.last_name or ''}"
        return QUESTION_1
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        return ConversationHandler.END

# Обработчики вопросов
async def question_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question_1"] = update.message.text
    await send_question(update, context, "Вопрос 2: Какие навыки у вас есть?", QUESTION_2)
    return QUESTION_2

async def question_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question_2"] = update.message.text
    await send_question(update, context, "Вопрос 3: Почему вы хотите вступить?", QUESTION_3)
    return QUESTION_3

async def question_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question_3"] = update.message.text
    await send_question(update, context, "Вопрос 4: Как вы узнали о нас?", QUESTION_4)
    return QUESTION_4

async def question_4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question_4"] = update.message.text
    await send_question(update, context, "Вопрос 5: Ваше сообщение админу?", QUESTION_5)
    return QUESTION_5

async def question_5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["question_5"] = update.message.text

    # Формирование сообщения админу
    message = (
        f"🚨 Новая заявка!\n"
        f"🆔 ID: {context.user_data['user_id']}\n"
        f"👤 Имя: {context.user_data['full_name']}\n"
        f"📱 Username: @{context.user_data['username']}\n"
        f"📝 Ответы:\n"
        f"1. {context.user_data.get('question_1', '-')}\n"
        f"2. {context.user_data.get('question_2', '-')}\n"
        f"3. {context.user_data.get('question_3', '-')}\n"
        f"4. {context.user_data.get('question_4', '-')}\n"
        f"5. {context.user_data.get('question_5', '-')}\n"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=message)
    await update.message.reply_text("✅ Заявка отправлена!")
    context.user_data.clear()
    return ConversationHandler.END

# Отмена анкеты
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Анкета отменена.")
    context.user_data.clear()
    return ConversationHandler.END

# Основная функция
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Обработчик запросов вступления и анкеты
    conv_handler = ConversationHandler(
        entry_points=[ChatJoinRequestHandler(handle_join_request)],
        states={
            QUESTION_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_1)],
            QUESTION_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_2)],
            QUESTION_3: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_3)],
            QUESTION_4: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_4)],
            QUESTION_5: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_5)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    
    # Настройка вебхука
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        secret_token=os.environ.get('SECRET_TOKEN', 'DEFAULT')
    )
