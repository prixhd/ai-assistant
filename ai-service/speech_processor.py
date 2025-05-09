import json
import os
import requests
from dagestani_phrases import add_dagestani_style

# Определяем хост Ollama из переменных окружения
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama:11434")

def process_query(query, store_data):
    """
    Обработка запроса пользователя и формирование ответа
    """
    # Проверка на простые запросы
    if "привет" in query.lower() or "здравствуй" in query.lower():
        return add_dagestani_style("Здравствуй! Чем могу помочь?")

    # Формируем промпт для ИИ
    prompt = _create_prompt(query, store_data)

    try:
        # Интеграция с Ollama вместо OpenAI
        response = _get_ai_response(prompt)

        # Добавляем дагестанский стиль
        styled_response = add_dagestani_style(response)
        return styled_response
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return add_dagestani_style("Извини, брат, что-то пошло не так. Спроси еще раз.")

def _create_prompt(query, store_data):
    """Создание промпта для ИИ"""
    # Сжимаем данные магазина для промпта
    prompt = f"""
    Ты голосовой ассистент для интернет-магазина "{store_data.get('storeName')}".
    Описание магазина: {store_data.get('storeDescription')}
    
    Запрос пользователя: "{query}"
    
    Ответь на запрос, используя только информацию о магазине:
    {json.dumps(store_data, ensure_ascii=False)}
    """

    return prompt

def _get_ai_response(prompt):
    """Получение ответа от Ollama вместо OpenAI"""
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": "llama2",
                "prompt": prompt,
                "temperature": 0.7,
                "max_tokens": 150
            }
        )

        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            print(f"Ошибка от Ollama API: {response.status_code} {response.text}")
            return "Извините, не удалось обработать ваш запрос."
    except Exception as e:
        print(f"Ошибка при запросе к Ollama API: {e}")
        return "Произошла техническая ошибка. Пожалуйста, попробуйте позже."