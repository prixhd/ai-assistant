FROM python:3.9-slim

WORKDIR /app

# Устанавливаем curl для healthcheck
RUN apt-get update && apt-get install -y curl && apt-get clean

# Установка зависимостей из requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Переменные окружения для API
ENV DEEPSEEK_API_KEY=sk-7d5ddde5e74d4e089dfaad352e4bcbc0
ENV DEEPSEEK_MODEL=deepseek-chat
ENV DEEPSEEK_API_URL=https://api.deepseek.com/v1

# Порт остается тем же
EXPOSE 5000

# Healthcheck для проверки работоспособности сервиса
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

CMD ["python", "app.py"]