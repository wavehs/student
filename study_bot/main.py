# study_bot/main.py

import time
import asyncio
from telegram.ext import Application

import config
import google_services
import ai_processor
import telegram_bot as tg_bot

async def check_emails_and_notify(app: Application):
    """
    Основной цикл, который проверяет почту, обрабатывает письма и отправляет уведомления.
    """
    chat_id = tg_bot.load_chat_id()
    if not chat_id:
        print("CHAT_ID не найден. Пользователь должен сначала запустить /start.")
        return

    print("Проверка почты...")
    creds = google_services.get_google_creds()
    new_emails = google_services.get_new_emails(creds)

    if not new_emails:
        print("Новых писем нет.")
        return

    print(f"Найдено {len(new_emails)} новых писем.")

    for email_summary in new_emails:
        email_id = email_summary['id']
        details = google_services.get_email_details(creds, email_id)

        if not details:
            continue

        ai_summary = ai_processor.process_slovak_email(details['original_text_sk'])
        full_data = {**details, **ai_summary}

        google_services.log_email_to_sheet(creds, full_data)
        print(f"Письмо {details['message_id']} залогировано в Google Sheet.")

        if full_data['category_ru'] != 'Инфо':
            await tg_bot.send_telegram_notification(
                bot_app=app,
                chat_id=chat_id,
                category=full_data['category_ru'],
                summary=full_data['summary_ru'],
                gmail_url=full_data['gmail_url'],
                gmail_message_id=full_data['message_id']
            )

async def main():
    """Главная функция, запускающая бота и цикл проверки почты."""
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(tg_bot.CommandHandler("start", tg_bot.start))
    application.add_handler(tg_bot.CommandHandler("week", tg_bot.week_summary))
    application.add_handler(tg_bot.CommandHandler("full", tg_bot.full_text))
    application.add_handler(tg_bot.MessageHandler(tg_bot.filters.TEXT & ~tg_bot.filters.COMMAND, tg_bot.handle_text_commands))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    print("Telegram-бот запущен.")

    while True:
        await check_emails_and_notify(application)
        await asyncio.sleep(config.CHECK_INTERVAL_SECONDS)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен вручную.")
