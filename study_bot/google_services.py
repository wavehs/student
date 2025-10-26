# study_bot/google_services.py

import os.path
import base64
import logging
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ИЗМЕНЕНО: Запрашиваем права на изменение писем, чтобы помечать их как прочитанные
SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/spreadsheets']

def get_google_creds():
    creds = None
    if os.path.exists(config.GOOGLE_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(config.GOOGLE_TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logging.info("Обновление токена доступа...")
            creds.refresh(Request())
        else:
            logging.info("Необходима новая авторизация пользователя...")
            flow = InstalledAppFlow.from_client_secrets_file(config.GOOGLE_CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(config.GOOGLE_TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            logging.info(f"Токен сохранен в файл: {config.GOOGLE_TOKEN_PATH}")
    return creds

def get_new_emails(creds):
    try:
        service = build('gmail', 'v1', credentials=creds)
        result = service.users().messages().list(userId='me', q=f'label:{config.GMAIL_LABEL} is:unread').execute()
        messages = result.get('messages', [])
        return messages
    except HttpError as error:
        logging.error(f"Ошибка при получении писем из Gmail: {error}")
        return []

def get_email_details(creds, message_id):
    try:
        service = build('gmail', 'v1', credentials=creds)
        message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        payload, headers = message['payload'], message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'Без темы')
        msg_id_header = next((h['value'] for h in headers if h['name'].lower() == 'message-id'), message_id)

        data = ''
        if 'parts' in payload:
            parts = payload['parts']
            part = next(filter(lambda p: p.get('mimeType') == 'text/plain', parts), parts[0])
            data = part['body'].get('data', '')
        elif 'body' in payload:
            data = payload['body'].get('data', '')

        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        gmail_url = f"https://mail.google.com/mail/u/0/#inbox/{message['threadId']}"
        original_text = f"Subject: {subject}\n\n{body}"

        return {
            'message_id': msg_id_header.strip('<>'),
            'gmail_url': gmail_url,
            'original_text_sk': original_text
        }
    except Exception as e:
        logging.error(f"Не удалось получить детали письма ID {message_id}: {e}")
        return None

def mark_email_as_read(creds, message_id):
    """Помечает письмо как прочитанное (удаляет метку 'UNREAD')."""
    try:
        service = build('gmail', 'v1', credentials=creds)
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        logging.info(f"Письмо ID {message_id} помечено как прочитанное.")
    except HttpError as error:
        logging.error(f"Не удалось пометить письмо ID {message_id} как прочитанное: {error}")

def log_email_to_sheet(creds, data):
    try:
        service = build('sheets', 'v4', credentials=creds)
        logging.info(f"Начинаю запись в Google Sheet ID: {config.GOOGLE_SHEET_ID}")
        row_data = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data.get('category_ru', 'N/A'),
            data.get('summary_ru', 'N/A'),
            data.get('gmail_url', 'N/A'),
            data.get('message_id', 'N/A'),
            data.get('original_text_sk', 'N/A'),
            ''
        ]
        body = {'values': [row_data]}
        result = service.spreadsheets().values().append(
            spreadsheetId=config.GOOGLE_SHEET_ID,
            range=f"{config.GOOGLE_SHEET_NAME}!A:G",
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        logging.info(f"Успешно записано {result.get('updates').get('updatedCells')} ячеек в таблицу.")
        return True
    except HttpError as error:
        logging.error(f"Ошибка при записи в Google Sheet: {error.content}")
        return False

# ... (остальные функции без изменений) ...
def find_email_by_telegram_message_id(creds, telegram_message_id):
    try:
        service = build('sheets', 'v4', credentials=creds)
        result = service.spreadsheets().values().get(
            spreadsheetId=config.GOOGLE_SHEET_ID,
            range=f"{config.GOOGLE_SHEET_NAME}!F:G"
        ).execute()
        values = result.get('values', [])
        for row in values:
            if len(row) == 2 and row[1] == telegram_message_id:
                return {'original_text_sk': row[0]}
        return None
    except HttpError as error:
        logging.error(f"Ошибка при поиске в Google Sheet: {error}")
        return None

def update_telegram_message_id(creds, gmail_message_id, telegram_message_id):
    try:
        service = build('sheets', 'v4', credentials=creds)
        result = service.spreadsheets().values().get(
            spreadsheetId=config.GOOGLE_SHEET_ID,
            range=f"{config.GOOGLE_SHEET_NAME}!E:E"
        ).execute()
        values = result.get('values', [])
        row_index = -1
        for i, row in enumerate(values):
            if row and row[0] == gmail_message_id:
                row_index = i + 1
                break

        if row_index != -1:
            range_to_update = f"{config.GOOGLE_SHEET_NAME}!G{row_index}"
            body = {'values': [[telegram_message_id]]}
            service.spreadsheets().values().update(
                spreadsheetId=config.GOOGLE_SHEET_ID,
                range=range_to_update,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            logging.info(f"Обновлен Telegram Message ID для строки {row_index}.")
    except HttpError as error:
        logging.error(f"Ошибка при обновлении Google Sheet: {error}")

def get_weekly_summary_from_sheet(creds):
    try:
        service = build('sheets', 'v4', credentials=creds)
        result = service.spreadsheets().values().get(
            spreadsheetId=config.GOOGLE_SHEET_ID,
            range=f"{config.GOOGLE_SHEET_NAME}!A:C"
        ).execute()
        values = result.get('values', [])
        if not values: return []

        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())

        weekly_summary = []
        for row in values[1:]:
            if len(row) >= 3:
                try:
                    timestamp = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
                    if start_of_week.date() <= timestamp.date() <= today.date():
                        weekly_summary.append({'category': row[1], 'summary': row[2]})
                except (ValueError, IndexError):
                    continue
        return weekly_summary
    except HttpError as error:
        logging.error(f"Ошибка при получении еженедельной сводки: {error}")
        return []
