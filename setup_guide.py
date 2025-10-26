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
GOOGLE_SHEET_NAME = 'Sheet1'  # Оставляем по умолчанию
GMAIL_LABEL = 'Образование'  # Оставляем по умолчанию

# --- AI (Gemini) Configuration ---
GEMINI_API_KEY = '{config_data['gemini_key']}'

# --- Bot Settings ---
CHECK_INTERVAL_SECONDS = 300  # 5 минут
"""

    # Убедимся, что директория study_bot существует
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
    print("Пожалуйста, подготовьте все необходимые ключи и ID.")

    # --- Шаг 1: Telegram Bot Token ---
    print_header("Шаг 1: Токен Telegram-бота")
    print("1. Откройте Telegram и найдите бота @BotFather.")
    print("2. Отправьте ему команду /newbot.")
    print("3. Следуйте инструкциям, чтобы создать нового бота.")
    print("4. В конце @BotFather пришлет вам токен. Скопируйте его.")
    config_data['telegram_token'] = get_user_input("➡️ Вставьте ваш Telegram Bot Token и нажмите Enter: ")

    # --- Шаг 2: Gemini API Key ---
    print_header("Шаг 2: API-ключ для Gemini")
    print("1. Перейдите в Google AI Studio: https://aistudio.google.com/app/apikey")
    print("2. Нажмите 'Create API key in new project'.")
    print("3. Скопируйте сгенерированный ключ.")
    config_data['gemini_key'] = get_user_input("➡️ Вставьте ваш Gemini API Key и нажмите Enter: ")

    # --- Шаг 3: Google API (credentials.json) ---
    print_header("Шаг 3: Настройка Google API (Gmail & Google Sheets)")
    print("Это самый важный шаг. Вам нужно получить файл 'credentials.json'.")
    print("\nИнструкция:")
    print("1. Перейдите в Google Cloud Console: https://console.cloud.google.com/apis/credentials")
    print("2. Убедитесь, что вы в правильном проекте (или создайте новый).")
    print("3. Нажмите '+ CREATE CREDENTIALS' -> 'OAuth client ID'.")
    print("4. Если спросит, настройте 'OAuth consent screen' (экран согласия):")
    print("   - Выберите 'External' и нажмите 'CREATE'.")
    print("   - Введите имя приложения (напр. 'StudyBot'), ваш email.")
    print("   - Пропустите все остальные шаги, нажимая 'SAVE AND CONTINUE', пока не вернетесь на страницу credentials.")
    print("5. Снова нажмите '+ CREATE CREDENTIALS' -> 'OAuth client ID'.")
    print("6. В 'Application type' выберите 'Desktop app' и дайте имя (напр. 'BotCredentials').")
    print("7. Нажмите 'CREATE'. Появится окно с вашими ID.")
    print("8. В списке 'OAuth 2.0 Client IDs' найдите только что созданный ID и справа нажмите на иконку скачивания (⬇️).")
    print("9. Переименуйте скачанный файл в 'credentials.json' и положите его в ту же папку, где находится этот скрипт.")

    input("\nНажмите Enter, когда будете готовы и файл 'credentials.json' будет в нужной папке...")

    # --- Шаг 4: Google Sheet ID ---
    print_header("Шаг 4: ID таблицы Google Sheet")
    print("1. Создайте новую таблицу Google Sheet: https://sheets.new")
    print("2. ВАЖНО: Дайте доступ к таблице вашему сервисному аккаунту.")
    print("   - Откройте файл 'credentials.json'. Найдите в нем строку 'client_email'.")
    print("   - Скопируйте этот email.")
    print("   - В Google Sheet нажмите 'Share' (Поделиться) и вставьте этот email, дав ему права 'Editor' (Редактор).")
    print("3. Теперь скопируйте ID таблицы из ее URL.")
    print("   - Пример URL: https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit")
    config_data['sheet_id'] = get_user_input("➡️ Вставьте ваш Google Sheet ID и нажмите Enter: ")

    # --- Создание config.py ---
    create_config_file(config_data)

    # --- Финальные инструкции ---
    print_header("Настройка завершена!")
    print("Теперь вам нужно установить зависимости и запустить бота.")
    print("Выполните в терминале следующие команды:")
    print("\n1. Установка библиотек:")
    print("   pip install google-api-python-client google-auth-oauthlib google-generativeai python-telegram-bot")
    print("\n2. Первый запуск бота:")
    print("   python study_bot/main.py")
    print("\nПосле запуска, бот попросит вас перейти по ссылке в браузере для авторизации в Google.")
    print("После этого в папке проекта появится файл 'token.json', и бот начнет работу.")
    print("Не забудьте написать вашему боту /start в Telegram!")

if __name__ == '__main__':
    main()
