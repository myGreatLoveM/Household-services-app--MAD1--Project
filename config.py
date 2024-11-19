import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR/".env")


class Config:
    APP = os.environ.get("FLASK_APP", "main")
    RUN_HOST = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
    RUN_PORT = os.environ.get("FLASK_RUN_PORT", 8000)
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "lvnkdbvjkbakvbkdbvjk")
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO=False
    STATIC_FOLDER = BASE_DIR/"static"
    TEMPLATES_FOLDER = BASE_DIR/"templates"
    MIGRATE_FOLDER = BASE_DIR/"migrations"
    USE_SESSION_FOR_NEXT = True
    ITEMS_PER_PAGE = 6


class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")


class ProductionConfig(Config):
    FLASK_ENV = 'production'


class TestingConfig(Config):
    FLASK_ENV = 'testing'
    TESTING = True
    SESSION_COOKIE_SECURE = True


