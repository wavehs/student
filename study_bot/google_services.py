# study_bot/google_services.py

import os.path
import base64
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/spreadsheets']

def get_google_creds():
    creds = None
    if os.path.exists(config.GOOGLE_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(config.GOOGLE_TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(config.GOOGLE_CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(config.GOOGLE_TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return creds

def get_new_emails(creds):
    try:
        service = build('gmail', 'v1', credentials=creds)
        result = service.users().messages().list(userId='me', q=f'label:{config.GMAIL_LABEL} is:unread').execute()
        messages = result.get('messages', [])
        return messages
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def get_email_details(creds, message_id):
    try:
        service = build('gmail', 'v1', credentials=creds)
        message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        payload, headers = message['payload'], message['payload']['headers']
        subject = next(h['value'] for h in headers if h['name'].lower() == 'subject')
        msg_id_header = next(h['value'] for h in headers if h['name'].lower() == 'message-id')

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
        print(f'An error occurred while getting email details: {e}')
        return None

def log_email_to_sheet(creds, data):
    try:
        service = build('sheets', 'v4', credentials=creds)
        row_data = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data['category_ru'],
            data['summary_ru'],
            data['gmail_url'],
            data['message_id'],
            data['original_text_sk'],
            '' # Placeholder for Telegram_Message_ID
        ]
        body = {'values': [row_data]}
        service.spreadsheets().values().append(
            spreadsheetId=config.GOOGLE_SHEET_ID,
            range=f"{config.GOOGLE_SHEET_NAME}!A:G",
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
    except HttpError as error:
        print(f'An error occurred while logging to sheet: {error}')

def find_email_by_telegram_message_id(creds, telegram_message_id):
    try:
        service = build('sheets', 'v4', credentials=creds)
        # Ищем в колонках F (Оригинал) и G (Telegram ID)
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
        print(f'An error occurred while searching sheet: {error}')
        return None

def update_telegram_message_id(creds, gmail_message_id, telegram_message_id):
    try:
        service = build('sheets', 'v4', credentials=creds)
        # Находим строку по gmail_message_id (колонка E)
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
            # Обновляем ячейку в колонке G
            range_to_update = f"{config.GOOGLE_SHEET_NAME}!G{row_index}"
            body = {'values': [[telegram_message_id]]}
            service.spreadsheets().values().update(
                spreadsheetId=config.GOOGLE_SHEET_ID,
                range=range_to_update,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
    except HttpError as error:
        print(f'An error occurred while updating sheet: {error}')

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
        print(f'An error occurred: {error}')
        return []
