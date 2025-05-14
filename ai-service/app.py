from flask import Flask, request, jsonify, make_response
import os
import requests
import time
import json
import random
from flask_cors import CORS

app = Flask(__name__)

# Правильная настройка CORS на уровне приложения
CORS(app, resources={r"/*": {"origins": "*"}})

response_cache = {}

# OpenRouter API настройки
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-r1")

# Старые настройки DeepSeek (оставляем для совместимости)
DEEPSEEK_API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-7d5ddde5e74d4e089dfaad352e4bcbc0")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

print(f"Используем OpenRouter API с моделью: {OPENROUTER_MODEL}")

# Более детальная настройка CORS
CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
}})

# Системный промпт остается без изменений
SYSTEM_PROMPT = """Ты - ассистент магазина 05.ру в Махачкале. Отвечай кратко, в дагестанском стиле.

О магазине: 05.ру - сеть магазинов электроники в Дагестане, адрес: пр. Имама Шамиля, 31. 
Часы работы: 9:00-21:00 ежедневно.

Ассортимент: 
- Смартфоны: iPhone (56-189 тыс), Samsung (23-129 тыс), Xiaomi (8-79 тыс)
- Ноутбуки: игровые (89-240 тыс), ультрабуки (49-180 тыс), офисные (32-65 тыс)
- ТВ и бытовая техника

Акции: 
- Скидки 30% на Samsung
- Кэшбэк 15% на Xiaomi
- Рассрочка 0-0-24 на ноутбуки

Доставка: бесплатно от 5000 руб по Махачкале.

также ссылка на сайт - https://05.ru/
"""

# Заглушки для ответов (на случай проблем с API)
# FALLBACK_RESPONSES = {
#     "привет": ["Ассалам алейкум, дорогой! Чем могу помочь?", "Здравствуй, брат! Что интересует?"],
#     "магазин": ["05.ру - лучший магазин электроники в Дагестане! Адрес: пр. Имама Шамиля, 31. Работаем с 9:00 до 21:00 каждый день.", "Наш магазин 05.ру - самый крутой в Махачкале! Приходи, не пожалеешь!"],
#     "акции": ["Сейчас у нас огонь-акции: 30% скидка на Samsung, 15% кэшбэк на Xiaomi и рассрочка 0-0-24 на ноутбуки!", "Брат, такие акции сейчас: Samsung -30%, кэшбэк 15% на Xiaomi, и ноутбуки в рассрочку без процентов!"],
#     "доставка": ["Доставка бесплатная от 5000 рублей по Махачкале, брат!", "Если заказ от 5000 рублей, доставим бесплатно по городу."],
#     "телефон": ["У нас есть iPhone (от 56 до 189 тысяч), Samsung (от 23 до 129 тысяч) и Xiaomi (от 8 до 79 тысяч). Что интересует?", "Брат, выбирай: iPhone, Samsung, Xiaomi - все есть, разные цены!"],
#     "ноутбук": ["Есть игровые (от 89 до 240 тысяч), ультрабуки (от 49 до 180 тысяч) и офисные (от 32 до 65 тысяч). Какой нужен?", "Игровые, ультрабуки, офисные - все виды ноутбуков в наличии!"],
#     "часы": ["Работаем с 9:00 до 21:00 без выходных, брат!", "Магазин открыт каждый день с 9 утра до 9 вечера."],
#     "адрес": ["Наш адрес: проспект Имама Шамиля, 31, Махачкала.", "Приходи на Шамиля, 31 - это в центре Махачкалы."],
#     "контакт": ["Звони нам: +7 (8722) 55-55-55 или пиши на info@05.ru", "Телефон магазина: +7 (8722) 55-55-55, почта: info@05.ru"]
# }

def process_content(content):
    """Обработка контента от OpenRouter API"""
    return content.replace('<think>', '').replace('</think>', '')

def generate_with_openrouter(message):
    """Генерация ответа с помощью OpenRouter API"""
    # Проверка кэша
    if message in response_cache:
        print("Ответ из кэша")
        return response_cache[message]

    try:
        # Формируем запрос к OpenRouter API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        # Добавляем инструкцию для модели, чтобы избежать опечаток
        enhanced_system_prompt = SYSTEM_PROMPT + "\n\nВажно: пиши без опечаток, проверяй текст перед отправкой. Не используй слово 'undefined'."

        data = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 800,  # Значительно увеличиваем лимит токенов
            "stream": False
        }

        print(f"Отправляем запрос к OpenRouter API с моделью {OPENROUTER_MODEL}: {message}")

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )

        print(f"OpenRouter response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            assistant_message = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Обработка контента
            assistant_message = process_content(assistant_message)

            # Удаляем "undefined" из ответа
            assistant_message = assistant_message.replace("undefined", "")

            # Проверка на обрезанный ответ
            if assistant_message.endswith(("приез", "прие", "при", "пр", "п")):
                assistant_message = assistant_message + "жай в магазин на пр. Имама Шамиля, 31!"

            # Проверка на пустой или некорректный ответ
            if not assistant_message or assistant_message.strip() == "" or len(set(assistant_message)) <= 2:
                return "Извините, не удалось получить корректный ответ. Пожалуйста, попробуйте другой вопрос."

            # Сохраняем ответ в кэш
            response_cache[message] = assistant_message
            return assistant_message
        else:
            print(f"Ошибка при генерации: {response.status_code}")
            if hasattr(response, 'text'):
                print(f"Response text: {response.text}")

            error_message = f"Извините, произошла ошибка при обработке запроса (код {response.status_code}). Пожалуйста, попробуйте позже."
            return error_message
    except Exception as e:
        print(f"Ошибка при запросе к OpenRouter API: {e}")
        error_message = f"Извините, произошла техническая ошибка. Пожалуйста, попробуйте позже."
        return error_message

# Оставляем старую функцию для совместимости
def check_deepseek_availability():
    """Проверка доступности API (теперь проверяем OpenRouter)"""
    try:
        # Простой запрос для проверки доступности API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            print("OpenRouter API доступен")
            return True
        else:
            print(f"Ошибка при проверке OpenRouter API: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Ошибка при подключении к OpenRouter API: {e}")
        return False

def clean_response(text):
    """Очистка ответа от возможных проблем"""
    if not isinstance(text, str):
        return str(text)

    # Удаляем "undefined"
    text = text.replace("undefined", "")

    # Исправление типичных опечаток
    common_typos = {
        "Врианты": "Варианты",
        "Заскамиь": "Заскочи",
        "хошь": "хочешь",
        "тыщ": "тысяч",
        "Всь": "Вот",
        "Валейкум": "Ваалейкум",
        "халяль-гаджет": "хороший гаджет"
    }

    for typo, correction in common_typos.items():
        text = text.replace(typo, correction)

    # Проверка на обрезанный ответ
    if text.endswith(("приез", "прие", "при", "пр", "п")):
        text = text + "жай в магазин на пр. Имама Шамиля, 31!"

    return text

@app.route('/process', methods=['POST', 'OPTIONS'])
def process():
    print(f"Received {request.method} request to /process")

    # ВАЖНО: Явно обрабатываем OPTIONS запросы
    if request.method == 'OPTIONS':
        return '', 204  # No Content для OPTIONS запросов

    try:
        data = request.json
        message = data.get('message', '')
        print(f"Received message: {message}")

        # Получаем ответ от OpenRouter API
        result = generate_with_openrouter(message)

        # Если результат пустой, возвращаем сообщение об ошибке
        if not result:
            result = "Извините, сервис временно недоступен. Пожалуйста, попробуйте позже."

        # Очищаем результат
        result = clean_response(result)

        # Явно удаляем "undefined" в конце
        if result.endswith("undefined"):
            result = result[:-9]  # Удаляем "undefined"

        print(f"Sending response: {result[:100]}...")
        return jsonify({"response": result})
    except Exception as e:
        print(f"General error: {e}")
        return jsonify({"error": f"Произошла ошибка: {str(e)}"}), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/', methods=['GET'])
def home():
    # Проверка работоспособности
    if check_deepseek_availability():
        return f"AI Service is running! Using OpenRouter model: {OPENROUTER_MODEL}"
    else:
        return "AI Service is running, but OpenRouter API is not available."

if __name__ == '__main__':
    # Проверяем доступность API
    for attempt in range(3):
        print(f"Попытка соединения с OpenRouter API ({attempt+1}/3)...")
        if check_deepseek_availability():
            print("Соединение с OpenRouter API установлено")
            break
        else:
            print("Не удалось подключиться к OpenRouter API")
            time.sleep(5)  # Ждем 5 секунд перед повторной попыткой

    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)