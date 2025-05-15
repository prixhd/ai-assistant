from flask import Flask, request, jsonify, make_response
import os
import requests
import time
import json
from flask_cors import CORS
import uuid

app = Flask(__name__)

# Правильная настройка CORS на уровне приложения
CORS(app, resources={r"/*": {"origins": "*"}})

# Кэш ответов
response_cache = {}

# Хранилище диалогов (в реальном приложении лучше использовать базу данных)
# Структура: {session_id: [{"role": "user/assistant", "content": "message"}, ...]}
conversations = {}

# OpenRouter API настройки
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-r1")

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


всю недостающую информацию бери только с сайта https://05.ru/
Важно: пиши без опечаток, проверяй текст перед отправкой. Не используй слово 'undefined'.
"""

def process_content(content):
    """Обработка контента от OpenRouter API"""
    return content.replace('<think>', '').replace('</think>', '')

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

def generate_with_openrouter(message, session_id):
    """Генерация ответа с помощью OpenRouter API с учетом истории диалога"""
    try:
        # Формируем запрос к OpenRouter API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        # Формируем сообщения для API, включая историю диалога
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Добавляем историю диалога, если она есть
        if session_id in conversations:
            # Ограничиваем историю последними 10 сообщениями, чтобы не превысить лимиты токенов
            history = conversations[session_id][-10:]
            messages.extend(history)

        # Добавляем текущее сообщение пользователя
        messages.append({"role": "user", "content": message})

        data = {
            "model": OPENROUTER_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 800,
            "stream": False
        }

        print(f"Отправляем запрос к OpenRouter API с моделью {OPENROUTER_MODEL}: {message}")
        print(f"История диалога: {len(messages) - 1} сообщений")

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
            assistant_message = clean_response(assistant_message)

            # Проверка на пустой или некорректный ответ
            if not assistant_message or assistant_message.strip() == "" or len(set(assistant_message)) <= 2:
                return "Извините, не удалось получить корректный ответ. Пожалуйста, попробуйте другой вопрос."

            # Сохраняем сообщение пользователя и ответ ассистента в историю диалога
            if session_id not in conversations:
                conversations[session_id] = []

            conversations[session_id].append({"role": "user", "content": message})
            conversations[session_id].append({"role": "assistant", "content": assistant_message})

            # Выводим текущую историю диалога для отладки
            print(f"Текущая история диалога для сессии {session_id}:")
            for msg in conversations[session_id]:
                print(f"- {msg['role']}: {msg['content'][:30]}...")

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

def check_api_availability():
    """Проверка доступности OpenRouter API"""
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

@app.route('/process', methods=['POST', 'OPTIONS'])
def process():
    print(f"Received {request.method} request to /process")

    # ВАЖНО: Явно обрабатываем OPTIONS запросы
    if request.method == 'OPTIONS':
        return '', 204  # No Content для OPTIONS запросов

    try:
        data = request.json
        message = data.get('message', '')
        session_id = data.get('session_id', '')

        # Если session_id не передан, создаем новый
        if not session_id:
            session_id = str(uuid.uuid4())
            print(f"Создана новая сессия: {session_id}")

        print(f"Received message: {message} (session: {session_id})")

        # Получаем ответ от OpenRouter API с учетом истории диалога
        result = generate_with_openrouter(message, session_id)

        # Если результат пустой, возвращаем сообщение об ошибке
        if not result:
            result = "Извините, сервис временно недоступен. Пожалуйста, попробуйте позже."

        print(f"Sending response: {result[:100]}...")
        return jsonify({
            "response": result,
            "session_id": session_id  # Возвращаем session_id клиенту
        })
    except Exception as e:
        print(f"General error: {e}")
        return jsonify({"error": f"Произошла ошибка: {str(e)}"}), 500

@app.route('/clear-session', methods=['POST', 'OPTIONS'])
def clear_session():
    """Очистка истории диалога для указанной сессии"""
    print(f"Received {request.method} request to /clear-session")

    # ВАЖНО: Явно обрабатываем OPTIONS запросы
    if request.method == 'OPTIONS':
        return '', 204  # No Content для OPTIONS запросов

    try:
        data = request.json
        session_id = data.get('session_id', '')

        if session_id and session_id in conversations:
            conversations[session_id] = []
            print(f"Очищена история диалога для сессии: {session_id}")
            return jsonify({"success": True, "message": "История диалога очищена"})
        else:
            print(f"Сессия не найдена: {session_id}")
            # Возвращаем успех даже если сессия не найдена, чтобы не блокировать клиента
            return jsonify({"success": True, "message": "Сессия не найдена или уже очищена"})
    except Exception as e:
        print(f"Error clearing session: {e}")
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
    if check_api_availability():
        return f"AI Service is running! Using OpenRouter model: {OPENROUTER_MODEL}"
    else:
        return "AI Service is running, but OpenRouter API is not available."

if __name__ == '__main__':
    # Проверяем доступность API
    for attempt in range(3):
        print(f"Попытка соединения с OpenRouter API ({attempt+1}/3)...")
        if check_api_availability():
            print("Соединение с OpenRouter API установлено")
            break
        else:
            print("Не удалось подключиться к OpenRouter API")
            time.sleep(5)  # Ждем 5 секунд перед повторной попыткой

    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)