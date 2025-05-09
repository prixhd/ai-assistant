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

# Определяем хост Ollama из переменных окружения
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
AVAILABLE_MODEL = os.environ.get('MODEL_NAME', 'tinyllama')

# Модель по умолчанию (компактнее, чем llama2)
DEFAULT_MODEL = "tinyllama"
print(f"Используем Ollama по адресу: {OLLAMA_HOST}")

# Системный промпт остается без изменений
# Более короткий системный промпт для TinyLlama
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

# Проверка и загрузка модели в Ollama
def ensure_model_available():
    try:
        # Проверяем доступные модели
        response = requests.get(f"{OLLAMA_HOST}/api/tags")
        print(f"Ollama API response: {response.status_code}")

        if response.status_code == 200:
            models = response.json().get("models", [])
            # Выводим список доступных моделей
            print(f"Available models: {[model['name'] for model in models]}")

            # Проверяем наличие нужных моделей
            available_models = [model["name"] for model in models]

            # Сначала проверяем llama2
            if "llama2" in available_models:
                print("Модель llama2 уже загружена")
                return "llama2"

            # Затем проверяем tinyllama
            elif "tinyllama" in available_models:
                print("Модель tinyllama уже загружена")
                return "tinyllama"

            # Если нет нужных моделей, пробуем загрузить tinyllama (она меньше)
            print(f"Загружаем модель {DEFAULT_MODEL}...")
            pull_response = requests.post(
                f"{OLLAMA_HOST}/api/pull",
                json={"name": DEFAULT_MODEL},
                timeout=300  # 5 минут таймаут на загрузку
            )

            if pull_response.status_code == 200:
                print(f"Модель {DEFAULT_MODEL} успешно загружена")
                return DEFAULT_MODEL
            else:
                print(f"Ошибка при загрузке модели: {pull_response.status_code}")
                print(pull_response.text)
                return None
        else:
            print(f"Ошибка при получении тегов: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ошибка при работе с Ollama API: {e}")
        return None

# Глобальная переменная для хранения названия доступной модели
AVAILABLE_MODEL = None

# Генерация ответа с помощью Ollama API
def generate_with_ollama(message):
    global AVAILABLE_MODEL, response_cache

    # Проверка кэша
    if message in response_cache:
        print("Ответ из кэша")
        return response_cache[message]

    # Если модель еще не определена, попробуем найти доступную
    if not AVAILABLE_MODEL:
        AVAILABLE_MODEL = ensure_model_available()
        if not AVAILABLE_MODEL:
            print("Не удалось найти или загрузить модель")
            return None

    try:
        prompt = f"{SYSTEM_PROMPT}\n\nКлиент: {message}\n\nАссистент:"
        print(f"Sending to Ollama model {AVAILABLE_MODEL}: {message}")

        first_request_timeout = 30 if message not in response_cache else 15

        # И используйте его:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": AVAILABLE_MODEL,
                "prompt": prompt,
                "temperature": 0.7,
                "max_tokens": 100,
                "top_p": 0.9
            },
            timeout=first_request_timeout  # Используем увеличенный таймаут для первого запроса
        )

        print(f"Ollama response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json().get("response", "")
            # Сохраняем ответ в кэш
            if result:
                response_cache[message] = result
            return result
        else:
            print(f"Ошибка при генерации: {response.status_code}")
            if hasattr(response, 'text'):
                print(f"Response text: {response.text}")

            # Если модель не найдена, сбрасываем переменную AVAILABLE_MODEL
            if response.status_code == 404:
                AVAILABLE_MODEL = None

            return None
    except Exception as e:
        print(f"Ошибка при запросе к Ollama API: {e}")
        return None

# Заглушка для тестирования без модели
def mock_response(message):
    message = message.lower()

    if "iphone" in message or "айфон" in message:
        return "Валлах, у нас отличный выбор iPhone! В наличии модели от iPhone 13 до 15 Pro Max, цены от 56 000 до 189 000 рублей."

    elif "акци" in message or "скидк" in message:
        return "Машаллах, сейчас у нас 'Весенняя распродажа' - скидки до 30% на технику Samsung, кэшбэк 15% на смартфоны Xiaomi, и рассрочка 0-0-24 на ноутбуки."

    elif "цен" in message:
        return "Цены в нашем магазине очень разные, зависит что именно тебя интересует. Смартфоны от 8 900, ноутбуки от 32 000, телевизоры от 19 900 рублей."

    elif "магазин" in message:
        return "05.ру - крупнейшая сеть магазинов электроники в Дагестане. Главный магазин в Махачкале на пр. Имама Шамиля, 31. Работаем ежедневно с 9:00 до 21:00."

    else:
        return "Спасибо за обращение в магазин 05.ру! Я могу рассказать о нашем ассортименте, акциях, доставке и сервисе. Что именно вас интересует, уважаемый?"

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

        # Пытаемся получить ответ от Ollama
        result = generate_with_ollama(message)

        # Если ответ не получен, используем заглушку
        if result is None:
            print("Using mock response")
            result = mock_response(message)

        print(f"Sending response: {result[:100]}...")
        return jsonify({"response": result})
    except Exception as e:
        print(f"General error: {e}")
        return jsonify({"error": f"Произошла ошибка: {str(e)}"}), 500

@app.route('/', methods=['GET'])
def home():
    # Проверка работоспособности
    model = ensure_model_available()
    if model:
        return f"AI Service is running! Available model: {model}"
    else:
        return "AI Service is running, but no models are available."

if __name__ == '__main__':
    # Ждем запуска Ollama
    for attempt in range(3):
        print(f"Попытка соединения с Ollama ({attempt+1}/3)...")
        try:
            response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
            print(f"Соединение с Ollama установлено: {response.status_code}")
            time.sleep(2)  # Даем время на инициализацию
            break
        except Exception as e:
            print(f"Ошибка соединения: {e}")
            time.sleep(10)  # Ждем 10 секунд перед повторной попыткой

    # Предварительно проверяем доступность модели
    AVAILABLE_MODEL = ensure_model_available()
    if AVAILABLE_MODEL:
        print(f"Будет использоваться модель: {AVAILABLE_MODEL}")
    else:
        print("Ни одна модель не доступна, но сервис будет запущен с заглушками")

    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)