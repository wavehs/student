# study_bot/main.py

import asyncio
import logging
from telegram.ext import Application

import config
import google_services
import ai_processor
import telegram_bot as tg_bot

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def check_emails_and_notify(app: Application):
    """
    Основной цикл, который проверяет почту, обрабатывает письма и отправляет уведомления.
    """
    chat_id = tg_bot.load_chat_id()
    if not chat_id:
        logging.warning("CHAT_ID не найден. Пользователь должен сначала запустить /start.")
        return

    logging.info("Начинаю проверку почты...")
    creds = google_services.get_google_creds()
    new_emails = google_services.get_new_emails(creds)

    if not new_emails:
        logging.info("Новых писем не найдено.")
        return

    logging.info(f"Обнаружено {len(new_emails)} новых писем.")

    for email_summary in new_emails:
        email_id = email_summary['id']
        logging.info(f"Обрабатываю письмо с ID: {email_id}")
        details = google_services.get_email_details(creds, email_id)

        if not details:
            logging.warning(f"Не удалось получить детали для письма ID: {email_id}. Пропускаю.")
            continue

        ai_summary = ai_processor.process_slovak_email(details['original_text_sk'])
        full_data = {**details, **ai_summary}

        logging.info(f"Письмо ID {email_id} классифицировано как '{full_data.get('category_ru', 'N/A')}'.")

        if google_services.log_email_to_sheet(creds, full_data):
            logging.info(f"Письмо {details.get('message_id', email_id)} успешно залогировано.")
        else:
            logging.error(f"Не удалось залогировать письмо {details.get('message_id', email_id)}.")
            continue

        if full_data.get('category_ru', 'Инфо') != 'Инфо':
            logging.info(f"Отправка уведомления для письма ID {email_id}...")
            await tg_bot.send_telegram_notification(
                bot_app=app,
                chat_id=chat_id,
                category=full_data['category_ru'],
                summary=full_data['summary_ru'],
                gmail_url=full_data['gmail_url'],
                gmail_message_id=full_data['message_id']
            )

        # Помечаем письмо как прочитанное, чтобы не обрабатывать его снова
        google_services.mark_email_as_read(creds, email_id)

async def main():
    """Главная функция, запускающая бота и цикл проверки почты."""
    logging.info("Запуск Telegram-бота...")
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(tg_bot.CommandHandler("start", tg_bot.start))
    application.add_handler(tg_bot.CommandHandler("week", tg_bot.week_summary))
    application.add_handler(tg_bot.CommandHandler("full", tg_bot.full_text))
    application.add_handler(tg_bot.MessageHandler(tg_bot.filters.TEXT & ~tg_bot.filters.COMMAND, tg_bot.handle_text_commands))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    logging.info("Telegram-бот успешно запущен.")

    while True:
        try:
            await check_emails_and_notify(application)
            logging.info(f"Следующая проверка через {config.CHECK_INTERVAL_SECONDS} секунд.")
            await asyncio.sleep(config.CHECK_INTERVAL_SECONDS)
        except Exception as e:
            logging.critical(f"Критическая ошибка в основном цикле: {e}", exc_info=True)
            await asyncio.sleep(60)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен вручную.")
