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
            text="*Привет! Ответь на четыре вопроса для вступления* 🔍\n\nПервый: откуда ты узнал о нашем Telegram-канале/чате\?",
            parse_mode="MarkdownV2"
        )
        context.user_data['state'] = 'awaiting_name'
    except Exception as e:
        logging.error(f"Ошибка: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    state = user_data.get('state')

    if state == 'awaiting_name':
        user_data['name'] = update.message.text
        user_data['state'] = 'awaiting_age'
        await update.message.reply_text("В следующем сообщении напиши, пожалуйста, свой возраст и из какого ты города.")

    elif state == 'awaiting_age':
        if not update.message.text.isdigit():
            await update.message.reply_text("❌ Возраст должен быть числом. Попробуйте еще раз!")
            return
        user_data['age'] = update.message.text
        user_data['state'] = 'awaiting_city'
        await update.message.reply_text("Для чего ты хочешь вступить в «Гей-Рязань», что интересует здесь прежде всего\?\n\nМожно ответить кратко или развёрнуто \(как хочешь\)\.")

    elif state == 'awaiting_city':
        user_data['city'] = update.message.text
        user_data['state'] = 'awaiting_reason'
        await update.message.reply_text("Назови три причины, по которым мы не должны тебе отказать 🟧")

    elif state == 'awaiting_reason':
        user_data['reason'] = update.message.text
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"""🚨 Новая заявка\!
🟪 Откуда: {user_data['name']}
🟪 Возраст и город: {user_data['age']}
🟪 Интересы: {user_data['city']}
🟪 Плюсы: {user_data['reason']}
🆔 ID: {update.message.from_user.id}"""
        )
        await update.message.reply_text(
            "*✔ Заявка отправлена\!*\n\nПосле того, как заявка будет одобрена, «Гей\-Рязань» появится в списке твоих чатов Telegram\.\n\nЕсли возникнут дополнительные вопросы, тебе напишет наш админ\.",
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
