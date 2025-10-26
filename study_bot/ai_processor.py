# study_bot/ai_processor.py

import google.generativeai as genai
import config

# Конфигурируем API-ключ
genai.configure(api_key=config.GEMINI_API_KEY)

# Настройка модели
generation_config = {
  "temperature": 0.3,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Создаем модель
model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

def process_slovak_email(email_text_sk):
    """
    Обрабатывает текст словацкого письма: переводит, классифицирует и извлекает суть.
    Слова-исключения (prednashka, cvicenie, seminar, zapocet, skuska) не переводятся.
    """
    prompt_parts = [
        "TASK: You are an assistant for a student. Analyze the following email written in Slovak.",
        "1.  Translate the text to Russian. CRITICAL: Do NOT translate these specific Slovak words: 'prednashka', 'cvicenie', 'seminar', 'zapocet', 'skuska'. They must remain in the original Latin script.",
        "2.  Based on the translated content, classify the email into one of these categories (in Russian): 'Отмена', 'Перенос', 'Дедлайн', 'Задание', 'Инфо'.",
        "3.  Extract key information: subject name, date, time, and topic.",
        "4.  Create a concise summary (Суть_RU) in Russian, incorporating the extracted information and the untranslated Slovak words.",
        "\nOUTPUT FORMAT: Provide the output in a structured format, using '::' as a separator.",
        "Category_RU::[Your Classification]\nSummary_RU::[Your Summary]",
        "\n---",
        f"\nEMAIL TEXT:\n{email_text_sk}",
    ]

    try:
        response = model.generate_content(prompt_parts)

        # Разбираем ответ модели
        results = {}
        for line in response.text.split('\n'):
            if '::' in line:
                key, value = line.split('::', 1)
                key = key.strip().lower()
                results[key] = value.strip()

        return {
            'category_ru': results.get('category_ru', 'Инфо'),
            'summary_ru': results.get('summary_ru', 'Не удалось извлечь суть.')
        }

    except Exception as e:
        print(f"An error occurred during AI processing: {e}")
        return {
            'category_ru': 'Инфо',
            'summary_ru': 'Ошибка при обработке текста письма.'
        }


def translate_slovak_to_russian_full(text_sk):
    """
    Выполняет полный перевод словацкого текста на русский язык, включая слова-исключения.
    """
    prompt_parts = [
        "TASK: You are a professional translator. Translate the following Slovak text to Russian.",
        "Ensure the translation is accurate and complete.",
        "\n---",
        f"\nSLOVAK TEXT:\n{text_sk}",
    ]

    try:
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        print(f"An error occurred during full translation: {e}")
        return "Ошибка перевода."
