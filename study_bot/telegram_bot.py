# study_bot/telegram_bot.py

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

import config
import google_services
import ai_processor

CHAT_ID_FILE = 'chat_id.txt'

def save_chat_id(chat_id):
    """Сохраняет chat_id в файл."""
    with open(CHAT_ID_FILE, 'w') as f:
        f.write(str(chat_id))

def load_chat_id():
    """Загружает chat_id из файла."""
    try:
        with open(CHAT_ID_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

# --- Функции-обработчики команд ---

async def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start. Сохраняет chat_id пользователя."""
    chat_id = update.message.chat_id
    save_chat_id(chat_id)
    print(f"Пользователь запустил бота. Chat ID {chat_id} сохранен.")

    keyboard = [
        [KeyboardButton("/week"), KeyboardButton("/full")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_text(
        "Привет! Я ваш учебный ассистент. Ваш ID был сохранен для отправки уведомлений.\n"
        "Используйте /week, чтобы получить сводку за неделю, или ответьте на уведомление командой /full для получения деталей.",
        reply_markup=reply_markup
    )


async def week_summary(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /week. Отправляет сводку за текущую неделю."""
    creds = google_services.get_google_creds()
    summary_data = google_services.get_weekly_summary_from_sheet(creds)

    if not summary_data:
        await update.message.reply_text("С понедельника по сегодня ничего важного не было.")
        return

    grouped_summary = {}
    for item in summary_data:
        category = item['category']
        if category not in grouped_summary:
            grouped_summary[category] = []
        grouped_summary[category].append(item['summary'])

    message_text = "Сводка с Понедельника по сегодня:\n"
    for category, summaries in grouped_summary.items():
        message_text += f"\n• {category}:\n"
        for summary in summaries:
            message_text += f"  - {summary}\n"

    await update.message.reply_text(message_text)


async def full_text(update: Update, context: CallbackContext) -> None:
    """
    Обработчик команды /full или ответа на сообщение.
    Отправляет полный текст письма (оригинал и перевод).
    """
    if not update.message.reply_to_message:
        await update.message.reply_text("Чтобы получить полный текст, ответьте на уведомление о письме командой /full.")
        return

    telegram_message_id = update.message.reply_to_message.message_id

    creds = google_services.get_google_creds()
    # Ищем email в Google Sheet по ID сообщения из Telegram
    email_data = google_services.find_email_by_telegram_message_id(creds, str(telegram_message_id))

    if not email_data:
        await update.message.reply_text("Не удалось найти связанное письмо. Возможно, это было не уведомление, или данные устарели.")
        return

    original_text_sk = email_data['original_text_sk']

    # Переводим полный текст
    translated_text_ru = ai_processor.translate_slovak_to_russian_full(original_text_sk)

    await update.message.reply_text(f"--- ОРИГИНАЛ (SK) ---\n\n{original_text_sk}")
    await update.message.reply_text(f"--- ПЕРЕВОД (RU) ---\n\n{translated_text_ru}")


async def handle_text_commands(update: Update, context: CallbackContext) -> None:
    """Обрабатывает текстовые команды, которые могут быть синонимами."""
    text = update.message.text.lower().strip()
    if text in ["/сводка", "че там по неделе?", "сводка"]:
        await week_summary(update, context)
    elif text in ["/text", "подробнее", "полный текст"]:
         await full_text(update, context)


async def send_telegram_notification(bot_app, chat_id, category, summary, gmail_url, gmail_message_id):
    """
    Отправляет уведомление в Telegram и обновляет Google Sheet с ID сообщения.
    """
    message_text = f"‼️ {category}: {summary}\n🔗 Ссылка на письмо: {gmail_url}"

    try:
        sent_message = await bot_app.bot.send_message(chat_id=chat_id, text=message_text)
        telegram_message_id = sent_message.message_id

        # Обновляем Google Sheet, добавляя ID сообщения Telegram
        creds = google_services.get_google_creds()
        google_services.update_telegram_message_id(creds, gmail_message_id, str(telegram_message_id))
        print(f"Уведомление отправлено. Telegram Message ID {telegram_message_id} записан в Google Sheet.")

    except Exception as e:
        print(f"Не удалось отправить уведомление в Telegram: {e}")
