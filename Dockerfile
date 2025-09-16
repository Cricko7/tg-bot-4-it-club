# Используем официальный Python образ
FROM python:3.12-slim

# Рабочая директория
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Устанавливаем переменные окружения (описание .env при деплое)
ENV PYTHONUNBUFFERED=1

# Команда запуска
CMD ["python", "bot.py"]
