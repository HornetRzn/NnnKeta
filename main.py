import os
from telegram import Update, Bot
from telegram.ext import (
    Application,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    ChatMemberHandler,
    filters
)

# Настройки
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
PORT = int(os.getenv("PORT", "443"))  # Используем порт 80

# Этапы анкетирования
QUESTION_1, QUESTION_2, QUESTION_3, QUESTION_4, QUESTION_5 = range(5)

async def start_quiz(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    context.user_data["user_id"] = user.id
    context.user_data["username"] = user.username or "Нет username"
    
    # Первый вопрос
    await update.effective_message.reply_text("Привет! Ответьте на вопросы для вступления:")
    await update.effective_message.reply_text("Вопрос 1: Как вас зовут?")
    return QUESTION_1

async def question_1(update: Update, context: CallbackContext) -> int:
    context.user_data["question_1"] = update.message.text
    await update.message.reply_text("Вопрос 2: Какие навыки у вас есть?")
    return QUESTION_2

async def question_2(update: Update, context: CallbackContext) -> int:
    context.user_data["question_2"] = update.message.text
    await update.message.reply_text("Вопрос 3: Почему вы хотите вступить?")
    return QUESTION_3

async def question_3(update: Update, context: CallbackContext) -> int:
    context.user_data["question_3"] = update.message.text
    await update.message.reply_text("Вопрос 4: Как вы узнали о нас?")
    return QUESTION_4

async def question_4(update: Update, context: CallbackContext) -> int:
    context.user_data["question_4"] = update.message.text
    await update.message.reply_text("Вопрос 5: Ваше сообщение админу?")
    return QUESTION_5

async def question_5(update: Update, context: CallbackContext) -> int:
    context.user_data["question_5"] = update.message.text

    user = update.message.from_user
    full_name = f"{user.first_name} {user.last_name or ''}"

    message = (
        f"Новая заявка:\n"
        f"ID: {context.user_data['user_id']}\n"
        f"Имя: {full_name}\n"
        f"Username: @{context.user_data['username']}\n"
        f"Ответы:\n"
        f"1. {context.user_data.get('question_1', '-')}\n"
        f"2. {context.user_data.get('question_2', '-')}\n"
        f"3. {context.user_data.get('question_3', '-')}\n"
        f"4. {context.user_data.get('question_4', '-')}\n"
        f"5. {context.user_data.get('question_5', '-')}\n"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=message)
    await update.message.reply_text("Заявка отправлена. Ждите ответа!")
    return ConversationHandler.END

async def handle_chat_member(update: Update, context: CallbackContext) -> None:
    new_chat_member = update.my_chat_member.new_chat_member
    if (
        new_chat_member
        and new_chat_member.status == "member"
        and update.my_chat_member.from_user.is_bot is False
    ):
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Привет! Ответьте на вопросы для вступления:",
        )
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Вопрос 1: Как вас зовут?",
        )
        context.user_data["state"] = QUESTION_1

async def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[],
        states={
            QUESTION_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_1)],
            QUESTION_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_2)],
            QUESTION_3: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_3)],
            QUESTION_4: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_4)],
            QUESTION_5: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_5)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.add_handler(ChatMemberHandler(handle_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))

    # Настройка Webhook для Render
    await application.bot.set_webhook(url=f"https://{os.getenv('RENDER_EXTERNAL_URL')}/{TOKEN}")
    await application.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
    )
    await application.run_polling()  # Или await application.run_webhook()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
