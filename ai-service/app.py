from flask import Flask, request, jsonify, make_response
import os
import requests
import time
import json
from flask_cors import CORS

app = Flask(__name__)

# Правильная настройка CORS на уровне приложения
CORS(app, resources={r"/*": {"origins": "*"}})

response_cache = {}

# Определяем хост DeepSeek из переменных окружения
DEEPSEEK_API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-7d5ddde5e74d4e089dfaad352e4bcbc0")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

print(f"Используем DeepSeek API по адресу: {DEEPSEEK_API_URL}")

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
"""

# Проверка доступности DeepSeek API
def check_deepseek_availability():
    try:
        # Простой запрос для проверки доступности API
        response = requests.get(
            f"{DEEPSEEK_API_URL}/models",
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            timeout=5
        )

        if response.status_code == 200:
            print("DeepSeek API доступен")
            return True
        else:
            print(f"Ошибка при проверке DeepSeek API: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Ошибка при подключении к DeepSeek API: {e}")
        return False

# Генерация ответа с помощью DeepSeek API
def generate_with_deepseek(message):
    # Проверка кэша
    if message in response_cache:
        print("Ответ из кэша")
        return response_cache[message]

    try:
        # Формируем запрос к DeepSeek API
        payload = {
            "model": DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 100,
            "top_p": 0.9
        }

        print(f"Отправляем запрос к DeepSeek модели {DEEPSEEK_MODEL}: {message}")

        response = requests.post(
            f"{DEEPSEEK_API_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )

        print(f"DeepSeek response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            assistant_message = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Сохраняем ответ в кэш
            if assistant_message:
                response_cache[message] = assistant_message
            return assistant_message
        else:
            print(f"Ошибка при генерации: {response.status_code}")
            if hasattr(response, 'text'):
                print(f"Response text: {response.text}")
            error_message = f"Ошибка API: {response.status_code}"
            return error_message
    except Exception as e:
        print(f"Ошибка при запросе к DeepSeek API: {e}")
        error_message = f"Техническая ошибка: {str(e)}"
        return error_message

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

        # Получаем ответ от DeepSeek
        result = generate_with_deepseek(message)

        # Если результат пустой, возвращаем сообщение об ошибке
        if not result:
            result = "Извините, сервис временно недоступен. Пожалуйста, попробуйте позже."

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
        return f"AI Service is running! Using DeepSeek model: {DEEPSEEK_MODEL}"
    else:
        return "AI Service is running, but DeepSeek API is not available."

if __name__ == '__main__':
    # Проверяем доступность DeepSeek API
    for attempt in range(3):
        print(f"Попытка соединения с DeepSeek API ({attempt+1}/3)...")
        if check_deepseek_availability():
            print("Соединение с DeepSeek API установлено")
            break
        else:
            print("Не удалось подключиться к DeepSeek API")
            time.sleep(5)  # Ждем 5 секунд перед повторной попыткой

    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
