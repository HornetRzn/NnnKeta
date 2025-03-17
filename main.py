import logging
import os
import re
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

def escape_markdown(text: str) -> str:
    """Экранирует спецсимволы MarkdownV2."""
    escape_chars = '_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    try:
        escaped_text = escape_markdown(
            "Привет! Ответь на четыре вопроса для вступления 🔍\n\n"
            "Первый: откуда ты узнал о нашем Telegram-канале/чате?"
        )
        await context.bot.send_message(
            chat_id=user.id,
            text=f"*{escaped_text}*",
            parse_mode="MarkdownV2"
        )
        context.user_data['state'] = 'awaiting_name'
    except Exception as e:
        logging.error(f"Ошибка: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    state = user_data.get('state')
    user = update.message.from_user

    if state == 'awaiting_name':
        user_data['name'] = update.message.text
        user_data['state'] = 'awaiting_age'
        await update.message.reply_text("В следующем сообщении напиши, пожалуйста, свой возраст и из какого ты города.")

    elif state == 'awaiting_age':
        if not re.search(r'\d+', update.message.text):
            await update.message.reply_text("❌ Возраст должен быть числом. Попробуйте еще раз!")
            return
        user_data['age'] = update.message.text
        user_data['state'] = 'awaiting_city'
        escaped_text = escape_markdown(
            "Для чего ты хочешь вступить в «Гей-Рязань», что интересует здесь прежде всего?\n\n"
            "Можно ответить кратко или развёрнуто (как хочешь)."
        )
        await update.message.reply_text(escaped_text, parse_mode="MarkdownV2")

    elif state == 'awaiting_city':
        user_data['city'] = update.message.text
        user_data['state'] = 'awaiting_reason'
        await update.message.reply_text("Назови три причины, по которым мы не должны тебе отказать 🟧")

    elif state == 'awaiting_reason':
        user_data['reason'] = update.message.text
        
        # Формирование информации о пользователе
        user_info = []
        if user.full_name:
            escaped_name = escape_markdown(user.full_name)
            user_info.append(f"👤 Имя: {escaped_name}")
        if user.username:
            escaped_username = escape_markdown(user.username)
            user_info.append(f"🔗 Username: @{escaped_username}")
        user_info.append(f"🆔 ID: {user.id}")

        admin_message = "\n".join([
            "🚨 Новая заявка!",
            *user_info,
            f"🟪 Откуда: {escape_markdown(user_data['name'])}",
            f"🟪 Возраст и город: {escape_markdown(user_data['age'])}",
            f"🟪 Интересы: {escape_markdown(user_data['city'])}",
            f"🟪 Плюсы: {escape_markdown(user_data['reason'])}"  # ✅ Исправлено: добавлена закрывающая скобка
        ])

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            parse_mode="MarkdownV2"
        )

        await update.message.reply_text(
            "✔ Заявка отправлена!\n\n"
            "После того, как заявка будет одобрена, «Гей-Рязань» появится в списке твоих чатов Telegram.\n\n"
            "Если возникнут дополнительные вопросы, тебе напишет наш админ.",
            parse_mode="MarkdownV2"
        )
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
