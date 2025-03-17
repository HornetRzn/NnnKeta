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
    """Экранирует все спецсимволы MarkdownV2."""
    escape_chars = '_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.chat_join_request.from_user
    try:
        text = (
            "**Привет! Ответь на четыре вопроса для вступления** 🔍\n"
            "Первый: откуда ты узнал о нашем Telegram-канале/чате?"
        )
        await context.bot.send_message(
            chat_id=user.id,
            text=text,
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
        await update.message.reply_text(
            escape_markdown("В следующем сообщении напиши, пожалуйста, свой возраст и из какого ты города."),
            parse_mode="MarkdownV2"
        )
    elif state == 'awaiting_age':
        if not re.search(r'\d+', update.message.text):
            await update.message.reply_text(
                escape_markdown("❌ Возраст должен быть числом. Попробуйте еще раз!"),
                parse_mode="MarkdownV2"
            )
            return
        user_data['age'] = update.message.text
        user_data['state'] = 'awaiting_city'
        text = escape_markdown(
            "Для чего ты хочешь вступить в «Гей-Рязань», что интересует здесь прежде всего?\n"
            "Можно ответить кратко или развёрнуто (как хочешь)."
        )
        await update.message.reply_text(text, parse_mode="MarkdownV2")
    elif state == 'awaiting_city':
        user_data['city'] = update.message.text
        user_data['state'] = 'awaiting_reason'
        await update.message.reply_text(escape_markdown("Назови три причины, по которым мы не должны тебе отказать 🟧"), parse_mode="MarkdownV2")
    elif state == 'awaiting_reason':
        user_data['reason'] = update.message.text
        user_info = []
        if user.full_name:
            user_info.append(f"👤 Имя: {escape_markdown(user.full_name)}")
        if user.username:
            user_info.append(f"🔗 Username: @{escape_markdown(user.username)}")
        user_info.append(f"🆔 ID: {user.id}")
        admin_message = "\n".join([
            escape_markdown("🚨 Новая заявка!"),
            *user_info,
            f"🟪 Откуда: {escape_markdown(user_data['name'])}",
            f"🟪 Возраст и город: {escape_markdown(user_data['age'])}",
            f"🟪 Интересы: {escape_markdown(user_data['city'])}",
            f"🟪 Плюсы: {escape_markdown(user_data['reason'])}"
        ])
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            parse_mode="MarkdownV2"
        )
        # Исправлено: "Заявка отправлена" теперь жирным
        success_text = (
            "✔ **Заявка отправлена**!\n"
            "После того, когда заявка будет одобрена, «Гей-Рязань» появится в списке твоих чатов Telegram.\n"
            "Если возникнут дополнительные вопросы, тебе напишет наш админ."
        )
        await update.message.reply_text(
            text=success_text,
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
