import os

from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """Base configuration"""

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
    ENV = os.getenv("ENV", "dev")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

    # Rate limiting
    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "true").lower() == "true"
    RATELIMIT_FAIL_OPEN = os.getenv("RATELIMIT_FAIL_OPEN", "true").lower() == "true"
    RATELIMIT_STRATEGY = os.getenv("RATELIMIT_STRATEGY", "fixed-window")
    _REDIS_AUTH = f":{REDIS_PASSWORD}@" if REDIS_PASSWORD else ""
    RATELIMIT_STORAGE_URI = os.getenv(
        "RATELIMIT_STORAGE_URI",
        f"redis://{_REDIS_AUTH}{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    )

    AUTH_LIMIT_PER_MINUTE = os.getenv("AUTH_LIMIT_PER_MINUTE", "5 per minute")
    AUTH_LIMIT_PER_5_MINUTES = os.getenv("AUTH_LIMIT_PER_5_MINUTES", "10 per 5 minutes")
    AUTH_LIMIT_PER_10_MINUTES = os.getenv(
        "AUTH_LIMIT_PER_10_MINUTES", "20 per 10 minutes"
    )
    AUTH_LIMIT_PER_HOUR = os.getenv("AUTH_LIMIT_PER_HOUR", "50 per hour")

    # RabbitMQ
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

    # API
    API_VERSION = os.getenv("API_VERSION", "1.0.0")
    CONTACT_NAME = os.getenv("CONTACT_NAME", "bicosteve")
    CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "***")
    API_BASE = os.getenv("API_VERSION_BASE", "/v0/api")

    # Docker subnet
    SUBNET = os.getenv("SUBNET", "172.25.0.0/16")
    RENDER_HOST = os.getenv(
        "RENDER_EXTERNAL_HOSTNAME", "job-board-api-esrv.onrender.com"
    )

    # UI Configs
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

    # Mail Configs
    EMAIL_FROM = os.getenv("EMAIL_FROM")
    MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
    MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
    MAILGUN_BASE_URL = os.getenv("MAILGUN_BASE_URL")

    # Sendgrid Configs
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "somestring")
    CELERY_BROKER_URL = "amqp://{user}:{password}@{host}:{port}/{vhost}".format(
        user=RABBITMQ_USER,
        password=RABBITMQ_PASSWORD,
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        vhost=RABBITMQ_VHOST,
    )
    CELERY_RESULT_BACKEND = (
        "redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}".format(
            redis_password=REDIS_PASSWORD,
            redis_host=REDIS_HOST,
            redis_port=REDIS_PORT,
            redis_db=REDIS_DB,
        )
    )


class DevelopmentConfig(BaseConfig):
    """Development Configurations"""

    DEBUG = True


class ProductionConfig(BaseConfig):
    """Production Configurations"""

    DEBUG = False


class DockerConfig(BaseConfig):
    """Docker Container Configurations"""

    DEBUG = True
    DEBUG = True
