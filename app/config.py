import os
from datetime import timedelta
from dotenv import load_dotenv

# Reads your .env file and loads it into os.environ
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret-not-for-prod")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "fallback-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    )
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)

class ProductionConfig(Config):
    DEBUG = False

config_map = {
    "development": DevelopmentConfig,
    "testing":     TestingConfig,
    "production":  ProductionConfig,
}

def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)