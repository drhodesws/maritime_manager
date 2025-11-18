import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')  # Use environment variable or default
    SQLALCHEMY_DATABASE_URI = 'sqlite:///maritime.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False