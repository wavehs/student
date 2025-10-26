# study_bot/config.py

# --- Telegram Bot Configuration ---
# Токен вашего Telegram-бота, полученный от @BotFather
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# --- Google API Configuration ---
# Путь к файлу credentials.json, полученному из Google Cloud Console
GOOGLE_CREDS_PATH = 'credentials.json'
# Путь для сохранения файла token.json, который будет создан после первой аутентификации
GOOGLE_TOKEN_PATH = 'token.json'
# ID вашего Google Sheet. Его можно найти в URL таблицы.
GOOGLE_SHEET_ID = 'YOUR_GOOGLE_SHEET_ID'
# Название листа в таблице
GOOGLE_SHEET_NAME = 'Sheet1'
# Метка в Gmail, которую бот будет мониторить
GMAIL_LABEL = 'Образование'

# --- AI (Gemini) Configuration ---
# Ваш API-ключ для Gemini
GEMINI_API_KEY = 'YOUR_GEMINI_API_KEY'

# --- Bot Settings ---
# Период проверки почты в секундах
CHECK_INTERVAL_SECONDS = 300  # 5 минут
