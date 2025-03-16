from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import os  # Добавьте это

# Настройки
TOKEN = os.getenv("TOKEN")  # Теперь берем из переменных окружения
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # ID должен быть числом

# Этапы анкетирования
QUESTION_1, QUESTION_2, QUESTION_3, QUESTION_4, QUESTION_5 = range(5)

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Привет! Ответьте на вопросы для вступления:")
    update.message.reply_text("Вопрос 1: Как вас зовут?")
    return QUESTION_1

def question_1(update: Update, context: CallbackContext) -> int:
    context.user_data["question_1"] = update.message.text
    update.message.reply_text("Вопрос 2: Какие навыки у вас есть?")
    return QUESTION_2

def question_2(update: Update, context: CallbackContext) -> int:
    context.user_data["question_2"] = update.message.text
    update.message.reply_text("Вопрос 3: Почему вы хотите вступить?")
    return QUESTION_3

def question_3(update: Update, context: CallbackContext) -> int:
    context.user_data["question_3"] = update.message.text
    update.message.reply_text("Вопрос 4: Как вы узнали о нас?")
    return QUESTION_4

def question_4(update: Update, context: CallbackContext) -> int:
    context.user_data["question_4"] = update.message.text
    update.message.reply_text("Вопрос 5: Ваше сообщение админу?")
    return QUESTION_5

def question_5(update: Update, context: CallbackContext) -> int:
    context.user_data["question_5"] = update.message.text

    user = update.message.from_user
    user_id = user.id
    username = user.username or "Нет username"
    full_name = f"{user.first_name} {user.last_name or ''}"

    message = (
        f"Новая заявка:\n"
        f"ID: {user_id}\n"
        f"Имя: {full_name}\n"
        f"Username: @{username}\n"
        f"Ответы:\n"
        f"1. {context.user_data.get('question_1', '-')}\n"
        f"2. {context.user_data.get('question_2', '-')}\n"
        f"3. {context.user_data.get('question_3', '-')}\n"
        f"4. {context.user_data.get('question_4', '-')}\n"
        f"5. {context.user_data.get('question_5', '-')}\n"
    )

    context.bot.send_message(chat_id=ADMIN_ID, text=message)
    update.message.reply_text("Заявка отправлена. Ждите ответа!")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Анкетирование отменено.")
    return ConversationHandler.END

def main() -> None:
    # Используем переменные окружения
    PORT = int(os.getenv("PORT", "8000"))  # Добавьте эту строку
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION_1: [MessageHandler(Filters.text & ~Filters.command, question_1)],
            QUESTION_2: [MessageHandler(Filters.text & ~Filters.command, question_2)],
            QUESTION_3: [MessageHandler(Filters.text & ~Filters.command, question_3)],
            QUESTION_4: [MessageHandler(Filters.text & ~Filters.command, question_4)],
            QUESTION_5: [MessageHandler(Filters.text & ~Filters.command, question_5)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    
    # Добавьте это для работы на Render
    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://nnnketa.onrender.com/{TOKEN}"
    )
    updater.idle()

if __name__ == '__main__':
    main()
