import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')  # Используем переменную окружения для секретного ключа
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:32313@localhost:5432/ptsd_test_db')  # Используем переменную окружения для базы данных
    SQLALCHEMY_TRACK_MODIFICATIONS = False

