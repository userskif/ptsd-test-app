import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:32313@localhost:5432/ptsd_test_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
