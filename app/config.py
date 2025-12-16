import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    '''Base configuration'''
    # General Flask
    DEBUG = bool(os.getenv("DEBUG", "False").lower() == "true")
    PORT = int(os.getenv("PORT", 5005))
    HOST = os.getenv("HOST", "0.0.0.0")
    SECRET_KEY = os.environ.get("SECRET_KEY", "mysuper_secret")
    EXPIRY_TIME = os.getenv("RESET_TIME", 3600)

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "mysupersecret")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_TOKEN_EXPIRY_HOURS = os.getenv("JWT_TOKEN_EXPIRY_HOURS", 48)

    # Database
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    DB_NAME = os.getenv("DB_NAME", "job-board-api")
    DB_PORT = int(os.getenv("DB_PORT", 3306))

    # Redis
    ENV = os.getenv('ENV', 'dev')
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

    # API
    API_VERSION = os.getenv("API_VERSION", "1.0.0")
    CONTACT_NAME = os.getenv("CONTACT_NAME", "bicosteve")
    CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "***")
    API_BASE = os.getenv("API_VERSION_BASE", "/v0/api")

    # Docker subnet
    SUBNET = os.getenv("SUBNET", "172.25.0.0/16")
    RENDER_HOST = os.getenv("RENDER_EXTERNAL_HOSTNAME",
                            "job-board-api-esrv.onrender.com")


class DevelopmentConfig(BaseConfig):
    '''Development Configurations'''
    DEBUG = True


class ProductionConfig(BaseConfig):
    '''Production Configurations'''
    DEBUG = False


class DockerConfig(BaseConfig):
    '''Docker Container Configurations'''
    DEBUG = True
