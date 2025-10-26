# setup_guide.py

import os

def print_header(title):
    """Выводит красивый заголовок."""
    print("\n" + "="*50)
    print(f"--- {title} ---")
    print("="*50)

def get_user_input(prompt):
    """Получает ввод от пользователя."""
    return input(prompt).strip()

def create_config_file(config_data):
    """Создает файл config.py на основе собранных данных."""
    config_content = f"""# study_bot/config.py
# Этот файл был сгенерирован автоматически скриптом setup_guide.py

# --- Telegram Bot Configuration ---
TELEGRAM_BOT_TOKEN = '{config_data['telegram_token']}'

# --- Google API Configuration ---
GOOGLE_CREDS_PATH = 'credentials.json'
GOOGLE_TOKEN_PATH = 'token.json'
GOOGLE_SHEET_ID = '{config_data['sheet_id']}'
GOOGLE_SHEET_NAME = 'Sheet1'
GMAIL_LABEL = 'Образование'

# --- AI (Gemini) Configuration ---
GEMINI_API_KEY = '{config_data['gemini_key']}'

# --- Bot Settings ---
CHECK_INTERVAL_SECONDS = 300
"""

    if not os.path.exists('study_bot'):
        os.makedirs('study_bot')

    with open('study_bot/config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    print("\n✅ Файл 'study_bot/config.py' успешно создан!")


def main():
    """Основная функция скрипта-настройщика."""
    config_data = {}

    print_header("Настройка Telegram-бота-ассистента")
    print("Этот скрипт поможет вам настроить вашего бота шаг за шагом.")

    # --- Шаг 1: Telegram Bot Token ---
    print_header("Шаг 1: Токен Telegram-бота")
    print("1. В Telegram найдите @BotFather и отправьте ему команду /newbot.")
    print("2. Следуйте инструкциям и скопируйте токен, который он вам пришлет.")
    config_data['telegram_token'] = get_user_input("➡️ Вставьте ваш Telegram Bot Token: ")

    # --- Шаг 2: Gemini API Key ---
    print_header("Шаг 2: API-ключ для Gemini")
    print("1. Перейдите в Google AI Studio: https://aistudio.google.com/app/apikey")
    print("2. Нажмите 'Create API key in new project' и скопируйте ключ.")
    config_data['gemini_key'] = get_user_input("➡️ Вставьте ваш Gemini API Key: ")

    # --- Шаг 3: Google API (credentials.json) ---
    print_header("Шаг 3: Настройка Google API (Gmail & Google Sheets)")
    print("Вам нужно получить файл 'credentials.json' из Google Cloud Console.")
    print("ПРИМЕЧАНИЕ: Боту потребуются права не только на чтение, но и на ИЗМЕНЕНИЕ писем (чтобы помечать их как прочитанные).")
    print("\nИнструкция:")
    print("1. Перейдите в Google Cloud Console: https://console.cloud.google.com/apis/credentials")
    print("2. Включите API:")
    print("   - Gmail API: https://console.cloud.google.com/apis/library/gmail.googleapis.com (Нажать 'Enable')")
    print("   - Google Sheets API: https://console.cloud.google.com/apis/library/sheets.googleapis.com (Нажать 'Enable')")
    print("3. Вернитесь на страницу Credentials и нажмите '+ CREATE CREDENTIALS' -> 'OAuth client ID'.")
    print("4. Если нужно, настройте 'OAuth consent screen' (экран согласия): выберите 'External', введите имя приложения, ваш email и сохраните.")
    print("5. Снова создайте 'OAuth client ID', выбрав 'Desktop app'.")
    print("6. Скачайте JSON-файл (иконка ⬇️) и переименуйте его в 'credentials.json'.")
    print("7. Положите этот файл в ту же папку, где находится этот скрипт.")

    input("\nНажмите Enter, когда файл 'credentials.json' будет в нужной папке...")

    # --- Шаг 4: Google Sheet ID ---
    print_header("Шаг 4: ID таблицы Google Sheet")
    print("1. Создайте новую таблицу: https://sheets.new")
    print("2. Скопируйте ID таблицы из ее URL (например, .../spreadsheets/d/THIS_IS_THE_ID/edit).")
    config_data['sheet_id'] = get_user_input("➡️ Вставьте ваш Google Sheet ID: ")

    # --- Создание config.py ---
    create_config_file(config_data)

    # --- Финальные инструкции ---
    print_header("Настройка завершена!")
    print("Теперь установите/обновите зависимости и запустите бота.")
    print("\n1. Установка библиотек:")
    print("   pip install --upgrade google-api-python-client google-auth-oauthlib google-generativeai python-telegram-bot")
    print("\n2. Первый запуск бота:")
    print("   python study_bot/main.py")
    print("\nВАЖНО: При первом запуске вам нужно будет авторизоваться в Google через браузер.")
    print("На экране согласия Google вы увидите, что приложение запрашивает права на просмотр и ИЗМЕНЕНИЕ писем. Это необходимо, чтобы бот не присылал дубликаты.")
    print("После авторизации не забудьте написать вашему боту /start в Telegram!")

if __name__ == '__main__':
    main()
