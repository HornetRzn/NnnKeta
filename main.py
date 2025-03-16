import logging
import os
from telegram import Update, helpers
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
            text=helpers.escape_markdown(
                "**Привет! Ответь на четыре вопроса для вступления** 💟\n\n"
                "1. Откуда ты узнал о нашем Telegram-канале/чате?",
                version=2
            ),
            parse_mode="MarkdownV2"
        )
        context.user_data['state'] = 'q1'
    except Exception as e:
        logging.error(f"Ошибка: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    state = user_data.get('state')

    if state == 'q1':
        user_data['source'] = update.message.text
        await update.message.reply_text(
            helpers.escape_markdown(
                "В следующем сообщении напиши, пожалуйста, свой возраст и из какого ты города.\n"
                "Пример: 25, Рязань",
                version=2
            ),
            parse_mode="MarkdownV2"
        )
        user_data['state'] = 'q2'

    elif state == 'q2':
        if "," not in update.message.text:
            await update.message.reply_text(
                helpers.escape_markdown("❌ Используй формат: возраст, город. Пример: 25, Рязань", version=2),
                parse_mode="MarkdownV2"
            )
            return
        age_city = update.message.text.split(",", 1)
        user_data['age'] = age_city[0].strip()
        user_data['city'] = age_city[1].strip()
        await update.message.reply_text(
            helpers.escape_markdown(
                "Для чего ты хочешь вступить в «Гей-Рязань», что интересует здесь прежде всего?\n"
                "(Можно ответить кратко или развёрнуто)",
                version=2
            ),
            parse_mode="MarkdownV2"
        )
        user_data['state'] = 'q3'

    elif state == 'q3':
        user_data['purpose'] = update.message.text
        await update.message.reply_text(
            helpers.escape_markdown(
                "Назови три причины, по которым мы не должны тебе отказать 🤔\n"
                "(Каждую причину можно писать с новой строки)",
                version=2
            ),
            parse_mode="MarkdownV2"
        )
        user_data['state'] = 'q4'

    elif state == 'q4':
        user_data['reasons'] = update.message.text
        try:
            escaped_source = helpers.escape_markdown(user_data['source'], version=2)
            escaped_age =
