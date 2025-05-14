FROM python:3.9-slim

WORKDIR /app

# Устанавливаем curl для healthcheck
RUN apt-get update && apt-get install -y curl && apt-get clean

# Установка зависимостей из requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Переменные окружения для API
ENV OPENROUTER_API_KEY=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
ENV OPENROUTER_MODEL=deepseek/deepseek-r1

# Старые переменные (оставляем для совместимости)
ENV DEEPSEEK_API_URL=https://api.deepseek.com/v1
ENV DEEPSEEK_MODEL=deepseek-chat

# Порт остается тем же
EXPOSE 5000

# Healthcheck для проверки работоспособности сервиса
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

CMD ["python", "app.py"]