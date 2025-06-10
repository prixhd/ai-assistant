from flask import Flask, request, jsonify, make_response
import os
import requests
import time
import json
from flask_cors import CORS
import uuid
import random

app = Flask(__name__)

# Правильная настройка CORS на уровне приложения
CORS(app, resources={r"/*": {"origins": "*"}})

# Кэш ответов
response_cache = {}

# Хранилище диалогов (в реальном приложении лучше использовать базу данных)
# Структура: {session_id: [{"role": "user/assistant", "content": "message"}, ...]}
conversations = {}

# DeepSeek API настройки
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-e997ae4e616585fa09ad825ac49eb8d1a30e56fb4e311c73a69869e64ea81768")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")

# Флаг для использования заглушек вместо реального API
USE_STUBS = os.environ.get("USE_STUBS", "True").lower() == "true"

print(f"Используем {'заглушки' if USE_STUBS else 'DeepSeek API с моделью: ' + DEEPSEEK_MODEL}")

CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
}})

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

СТРУКТУРА СТРАНИЦЫ САЙТА:
Вот основные элементы на странице сайта 05.ru и их ID:
- ID="main-header" - Шапка сайта с логотипом, поиском и контактами
- ID="search-box" - Поле поиска товаров
- ID="contacts" - Контактная информация в шапке
- ID="main-menu" - Главное меню навигации
- ID="smartphones" - Раздел "Смартфоны" в меню
- ID="laptops" - Раздел "Ноутбуки" в меню
- ID="tv" - Раздел "Телевизоры" в меню
- ID="appliances" - Раздел "Бытовая техника" в меню
- ID="accessories" - Раздел "Аксессуары" в меню
- ID="promo-section" - Секция с акциями и баннерами
- ID="samsung-promo" - Баннер со скидкой 30% на Samsung
- ID="featured-products" - Секция с популярными товарами
- ID="iphone-13" - Карточка товара iPhone 13
- ID="samsung-s21" - Карточка товара Samsung Galaxy S21
- ID="xiaomi-11t" - Карточка товара Xiaomi 11T
- ID="acer-nitro" - Карточка товара Acer Nitro 5
- ID="delivery-section" - Секция с информацией о доставке
- ID="main-footer" - Подвал сайта с дополнительной информацией

ВАЖНО: Когда тебя спрашивают о конкретном товаре или акции, указывай на соответствующий элемент на странице.
Для этого включай в свой ответ JSON-объект с полями:
- text: основной текст ответа
- highlightElement: ID элемента, который нужно подсветить

Например, если спрашивают о скидках на Samsung, твой ответ должен быть таким:

{ "text": "Валлах, брат, сейчас у нас большая скидка 30% на всю технику Samsung! Глянь вот на этот Samsung Galaxy S21 - цена упала с 69 990 ₽ до 48 993 ₽. Успей взять, пока не разобрали!", "highlightElement": "samsung-s21" }

Отвечай на вопросы о товарах, предоставляя информацию о конкретных товарах на странице с их ценами.
Не придумывай информацию о товарах, которых нет на странице.

Важно: пиши без опечаток, проверяй текст перед отправкой. Не используй слово 'undefined'.
"""

# Расширенные заглушки ответов по ключевым словам
KEYWORD_RESPONSES = {
    # Смартфоны - исправлены все варианты написания
    "iphone": {"text": "iPhone? Брат, у нас есть все модели! iPhone 15 Pro Max - 189 тысяч, iPhone 14 - 95 тысяч, iPhone 13 - 76 тысяч. Все оригинал, гарантия Apple 1 год. Хочешь посмотреть конкретную модель?", "highlightElement": "iphone-13"},
    "айфон": {"text": "Айфоны у нас самые свежие! iPhone 15 Pro - топ за 156 тысяч, iPhone 14 Plus - 105 тысяч. Можем и прошлые модели показать - дешевле будет. В рассрочку тоже можно оформить!", "highlightElement": "smartphones"},

    "samsung": {"text": "Samsung? Валлах, сейчас акция 30% на всё! Galaxy S23 Ultra был 129 тысяч, сейчас 90 тысяч! Galaxy S21 - 48 993 ₽ вместо 69 990 ₽. Fold и Flip тоже есть в наличии!", "highlightElement": "samsung-s21"},
    "самсунг": {"text": "Самсунг - отличный выбор, брат! S23 со скидкой, A54 за 35 тысяч - для тех, кто экономит. Galaxy Watch в подарок при покупке флагмана!", "highlightElement": "samsung-promo"},

    "xiaomi": {"text": "Xiaomi? Лучшая цена-качество! Xiaomi 13 Pro - 79 тысяч, Mi 11T - 39 990 ₽. Redmi Note 12 всего 23 тысячи! Плюс кэшбэк 15% на любой Xiaomi до конца месяца!", "highlightElement": "xiaomi-11t"},
    "сяоми": {"text": "Сяоми берут умные люди! POCO X5 Pro - 32 тысячи, камера как у флагмана. Redmi для родителей - от 15 тысяч. Наушники Mi Buds в подарок от 30 тысяч!", "highlightElement": "xiaomi-11t"},

    # Ноутбуки
    "ноутбук": {"text": "Ноутбуки на любой вкус! Игровые: MSI Katana - 115 тысяч, Acer Nitro 5 - 89 тысяч. Для работы: ASUS VivoBook - 45 тысяч, Lenovo IdeaPad - 38 тысяч. Рассрочка 0-0-24 на все модели!", "highlightElement": "laptops"},
    "macbook": {"text": "MacBook? Эээ, брат, это премиум! MacBook Air M2 - 135 тысяч, MacBook Pro 14 - 215 тысяч. Но они того стоят - батарея держит весь день, экран огонь! Студентам скидка 5%!", "highlightElement": "laptops"},
    "игровой": {"text": "Для игр что-то ищешь? ASUS ROG Strix - зверь за 165 тысяч, всё потянет! MSI GF63 - 95 тысяч, оптимальный вариант. Acer Nitro 5 - 89 тысяч, RTX 3050 внутри!", "highlightElement": "acer-nitro"},

    # Телевизоры
    "телевизор": {"text": "Телевизоры от 32 до 85 дюймов! Samsung QLED 55\" - 89 тысяч, LG OLED 65\" - 145 тысяч. Xiaomi 43\" всего 28 тысяч - для кухни самое то! Настройку и доставку делаем бесплатно!", "highlightElement": "tv"},
    "тв": {"text": "ТВ какой диагонали интересует? 55 дюймов самый популярный - от 45 тысяч. 4K уже стандарт, Full HD только в маленьких размерах. Smart TV везде, можно YouTube смотреть!", "highlightElement": "tv"},

    # Бытовая техника
    "холодильник": {"text": "Холодильники есть! Samsung с инвертором - 78 тысяч, 10 лет гарантия на компрессор. LG DoorCooling - 65 тысяч. Бюджетные Beko от 32 тысяч. Старый заберем бесплатно!", "highlightElement": "appliances"},
    "стиральн": {"text": "Стиральные машины - большой выбор! LG с прямым приводом - 48 тысяч, тихая очень. Samsung с паром - 52 тысячи, вещи как новые. Candy для дачи - 25 тысяч. Установка 3000 рублей!", "highlightElement": "appliances"},
    "микроволн": {"text": "Микроволновки от 5 до 12 тысяч! Samsung с грилем - 9500, LG соло - 6800. Есть встраиваемые для кухни - от 18 тысяч. Все с гарантией минимум год!", "highlightElement": "appliances"},
    "кондиционер": {"text": "Кондиционеры - лето близко, брат! Сплит-системы от 28 тысяч. Установка наша бригада делает - 8 тысяч под ключ. Мобильные кондиционеры тоже есть - от 19 тысяч, установка не нужна!", "highlightElement": "appliances"},

    # Аксессуары
    "наушники": {"text": "Наушники? AirPods Pro 2 - 28 тысяч, оригинал! Samsung Buds 2 Pro - 18 тысяч. JBL и Sony от 3 тысяч. Игровые HyperX - 12 тысяч. При покупке телефона скидка 20% на любые наушники!", "highlightElement": "accessories"},
    "чехол": {"text": "Чехлы на все модели! Оригинальные Apple - от 3 тысяч, силикон и кожа. Противоударные UAG - 2500. Обычные от 500 рублей. Стекла защитные тоже есть - от 800 рублей с установкой!", "highlightElement": "accessories"},
    "powerbank": {"text": "Power Bank нужен? Xiaomi 20000 mAh - 2800 рублей, два телефона зарядит. Baseus 30000 mAh - 4500, ноутбук можно заряжать! Компактные 10000 mAh от 1500 рублей!", "highlightElement": "accessories"},

    # Услуги
    "доставка": {"text": "Доставка бесплатная от 5000 рублей по всей Махачкале! До 5000 - всего 300 рублей. По районам Дагестана тоже возим - уточняй по телефону. Обычно привозим в день заказа или на следующий!", "highlightElement": "delivery-section"},
    "рассрочка": {"text": "Рассрочка есть на всё! 0-0-24 - это без первого взноса и переплат на 24 месяца. Нужен только паспорт, одобрение за 5 минут. Досрочное погашение в любой момент без штрафов!", "highlightElement": "promo-section"},
    "гарантия": {"text": "Гарантия официальная на всю технику! На телефоны - 1 год, на ноутбуки - от 1 до 3 лет. Бытовая техника - 2 года минимум. Расширенная гарантия тоже можно оформить - спокойнее будет!", "highlightElement": "main-footer"},
    "trade-in": {"text": "Trade-in? Конечно принимаем старые телефоны! Оценка прямо в магазине за 10 минут. iPhone принимаем дороже всех. Скидка на новый телефон до 30 тысяч в зависимости от модели!", "highlightElement": "promo-section"},

    # Контакты и общее
    "адрес": {"text": "Наш адрес: проспект Имама Шамиля, 31. Это в центре, рядом с ЦУМом. Парковка есть во дворе - бесплатная для покупателей. Работаем каждый день с 9:00 до 21:00!", "highlightElement": "contacts"},
    "телефон": {"text": "Звони на горячую линию: 8-800-555-05-05 - бесплатно по России! WhatsApp: +7-928-555-05-05 - можно фото товара скинуть. В магазине консультанты всё покажут и расскажут!", "highlightElement": "contacts"},
    "скидк": {"text": "Скидки сейчас огонь! Samsung -30%, Xiaomi кэшбэк 15%, на наушники -20% при покупке телефона. Студентам и пенсионерам дополнительная скидка 5%. В приложении еще больше акций!", "highlightElement": "promo-section"},
    "акци": {"text": "Акции меняются каждую неделю! Сейчас: Samsung со скидкой 30%, рассрочка 0-0-24 на всё, подарки при покупке от 50 тысяч. Подпишись на наш Telegram - там эксклюзивные предложения!", "highlightElement": "promo-section"}
}

# Расширенные общие ответы для заглушки
STUB_RESPONSES = [
    {"text": "Ассалам алейкум, дорогой! Добро пожаловать в 05.ру - лучший магазин электроники в Дагестане! Что тебя интересует - телефоны, ноутбуки, телевизоры? У нас сейчас большие скидки!", "highlightElement": "main-header"},
    {"text": "Валлах, брат, у нас самые лучшие цены в Махачкале! И гарантия официальная на всё. Что ищешь - для себя или в подарок?", "highlightElement": "featured-products"},
    {"text": "Слушай, у нас сейчас такие акции - сам в шоке! Samsung со скидкой 30%, на Xiaomi кэшбэк 15%. Приходи в магазин на Шамиля 31, всё покажем!", "highlightElement": "promo-section"},
    {"text": "Брат, скажи что нужно - подберем лучший вариант! Телефон, ноутбук, телевизор? Бюджет какой примерно? Можем и в рассрочку оформить без переплат!", "highlightElement": "main-menu"},
    {"text": "Дорогой, у нас честные цены и никакого обмана! Вся техника с официальной гарантией. Доставка бесплатная от 5000 рублей. Что конкретно интересует?", "highlightElement": "delivery-section"}
]

def generate_stub_response(message, session_id):
    """Генерация ответа с помощью заглушек без обращения к API"""
    try:
        # Приводим сообщение к нижнему регистру для поиска
        message_lower = message.lower()

        # Сначала ищем точные совпадения по ключевым словам
        for keyword, response in KEYWORD_RESPONSES.items():
            if keyword in message_lower:
                return json.dumps(response, ensure_ascii=False)

        # Если это приветствие
        greetings = ["привет", "салам", "здравствуй", "добрый", "ассалам"]
        if any(greeting in message_lower for greeting in greetings):
            return json.dumps({
                "text": "Ваалейкум ассалам, брат! Рад тебя видеть в 05.ру! Чем могу помочь? У нас отличные предложения на телефоны и ноутбуки!",
                "highlightElement": "main-header"
            }, ensure_ascii=False)

        # Если спрашивают о цене без указания товара
        if "цена" in message_lower or "сколько стоит" in message_lower or "почем" in message_lower:
            return json.dumps({
                "text": "Цены у нас самые выгодные! На что конкретно смотришь? Телефоны от 15 тысяч, ноутбуки от 32 тысяч, телевизоры от 25 тысяч. Назови модель - скажу точную цену!",
                "highlightElement": "featured-products"
            }, ensure_ascii=False)

        # Если не нашли подходящий ответ, возвращаем случайный
        response = random.choice(STUB_RESPONSES)
        return json.dumps(response, ensure_ascii=False)

    except Exception as e:
        print(f"Ошибка при генерации заглушки: {e}")
        return json.dumps({
            "text": "Извините, произошла техническая ошибка. Пожалуйста, попробуйте еще раз.",
            "highlightElement": "main-header"
        }, ensure_ascii=False)

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


def generate_with_deepseek(message, session_id):
    """Генерация ответа с помощью DeepSeek API с учетом истории диалога"""
    # Если включен режим заглушек, используем его вместо реального API
    if USE_STUBS:
        return generate_stub_response(message, session_id)

    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        # Формируем сообщения для API, включая историю диалога
        messages = []

        # Добавляем системный промпт
        messages.append({"role": "system", "content": SYSTEM_PROMPT})

        # Добавляем историю диалога, если она есть
        if session_id in conversations:
            # Ограничиваем историю последними 10 сообщениями
            history = conversations[session_id][-10:]
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Добавляем текущее сообщение пользователя
        messages.append({"role": "user", "content": message})

        data = {
            "model": DEEPSEEK_MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }

        print(f"Отправлен запрос к DeepSeek API с моделью {DEEPSEEK_MODEL}")
        print(f"История диалога: {len(messages)-2} сообщений")  # -2 для системного промпта и текущего сообщения

        response = requests.post(
            f"{DEEPSEEK_API_URL}/chat/completions",
            headers=headers,
            json=data
        )

        if response.status_code != 200:
            print(f"Ошибка API: {response.status_code} - {response.text}")
            return "Извините, произошла техническая ошибка. Пожалуйста, попробуйте позже."

        response_data = response.json()
        assistant_message = response_data["choices"][0]["message"]["content"]

        # Очистка ответа
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
    except Exception as e:
        print(f"Ошибка при запросе к DeepSeek API: {e}")
        error_message = f"Извините, произошла техническая ошибка. Пожалуйста, попробуйте позже."
        return error_message

def check_api_availability():
    """Проверка доступности DeepSeek API"""
    # Если включен режим заглушек, считаем API всегда доступным
    if USE_STUBS:
        return True

    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": DEEPSEEK_MODEL,
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 5
        }

        response = requests.post(
            f"{DEEPSEEK_API_URL}/chat/completions",
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            print("DeepSeek API доступен")
            return True
        else:
            print(f"Ошибка при проверке DeepSeek API: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Ошибка при подключении к DeepSeek API: {e}")
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

        # Получаем ответ от DeepSeek API с учетом истории диалога
        result = generate_with_deepseek(message, session_id)

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
        return '', 204  # No Content для OPTIONS запросы

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
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/', methods=['GET'])
def home():
    # Проверка работоспособности
    if USE_STUBS:
        return f"AI Service is running in STUB mode! No actual API calls will be made."
    elif check_api_availability():
        return f"AI Service is running! Using DeepSeek model: {DEEPSEEK_MODEL}"
    else:
        return "AI Service is running, but DeepSeek API is not available."

if __name__ == '__main__':
    # Проверяем доступность API только если не используем заглушки
    if not USE_STUBS:
        for attempt in range(3):
            print(f"Попытка соединения с DeepSeek API ({attempt+1}/3)...")
            if check_api_availability():
                print("Соединение с DeepSeek API установлено")
                break
            else:
                print("Не удалось подключиться к DeepSeek API")
                time.sleep(5)  # Ждем 5 секунд перед повторной попыткой
    else:
        print("Запуск в режиме заглушек. Проверка API не требуется.")

    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)