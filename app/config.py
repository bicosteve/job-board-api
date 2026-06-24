import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


def _normalize_path(path, default="/"):
    """Normalize a URL path so it starts with one slash and has no trailing slash."""
    path = (path or default or "/").strip()
    if not path.startswith("/"):
        path = f"/{path}"
    return path.rstrip("/") or "/"


def _normalize_prefix(path):
    """Normalize a mounted public prefix. Empty means the app is not mounted."""
    path = (path or "").strip()
    if not path or path == "/":
        return ""
    if not path.startswith("/"):
        path = f"/{path}"
    return path.rstrip("/")


def _join_url_paths(*parts):
    """Join URL path fragments without introducing duplicate slashes."""
    cleaned = [str(part).strip("/") for part in parts if part and str(part).strip("/")]
    return f"/{'/'.join(cleaned)}" if cleaned else "/"


class BaseConfig:
    """Base configuration"""

    # Env
    ENV = os.getenv("ENV", "dev")

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
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    REDIS_USERNAME = os.getenv("REDIS_USERNAME", "")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    REDIS_TLS = os.getenv("REDIS_TLS", "false").lower() == "true"
    REDIS_URL = os.getenv("REDIS_URL")  # prioritized over individual vars

    # RabbitMQ
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

    # API
    API_VERSION = os.getenv("API_VERSION", "1.0.0")
    CONTACT_NAME = os.getenv("CONTACT_NAME", "bicosteve")
    CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "devbico@gmail.com")

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

    # ===== Celery Urls

    # Celery — read directly from env, fall back to building from individual vars
    CELERY_BROKER_URL = os.getenv(
        "CELERY_BROKER_URL",
        "amqp://{user}:{password}@{host}:{port}/{vhost}".format(
            user=os.getenv("RABBITMQ_USER", "guest"),
            password=os.getenv("RABBITMQ_PASSWORD", "guest"),
            host=os.getenv("RABBITMQ_HOST", "localhost"),
            port=os.getenv("RABBITMQ_PORT", "5672"),
            vhost=os.getenv("RABBITMQ_VHOST", "/"),
        ),
    )

    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND",
        os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    )

    RABBITMQ_URL = os.getenv(
        "RABBITMQ_URL",
        os.getenv(
            "CELERY_BROKER_URL",
            "",
        ),
    )

    # Rate limiting
    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "true").lower() == "true"
    RATELIMIT_FAIL_OPEN = os.getenv("RATELIMIT_FAIL_OPEN", "true").lower() == "true"
    RATELIMIT_STRATEGY = os.getenv("RATELIMIT_STRATEGY", "fixed-window")
    _redis_auth = (
        f":{os.getenv('REDIS_PASSWORD')}@" if os.getenv("REDIS_PASSWORD") else ""
    )
    RATELIMIT_STORAGE_URI = os.getenv(
        "REDIS_URL",
        f"redis://{_redis_auth}{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/{os.getenv('REDIS_DB', 0)}",
    )

    AUTH_LIMIT_PER_MINUTE = os.getenv("AUTH_LIMIT_PER_MINUTE", "5 per minute")
    AUTH_LIMIT_PER_5_MINUTES = os.getenv("AUTH_LIMIT_PER_5_MINUTES", "10 per 5 minutes")
    AUTH_LIMIT_PER_10_MINUTES = os.getenv(
        "AUTH_LIMIT_PER_10_MINUTES", "20 per 10 minutes"
    )
    AUTH_LIMIT_PER_HOUR = os.getenv("AUTH_LIMIT_PER_HOUR", "50 per hour")

    # Flask route base. Your current nginx config preserves /job-board-api when
    # proxying to gunicorn, and local testing also uses /job-board-api/... URLs.
    # Therefore the Flask routes must include the public prefix by default.
    API_BASE = _normalize_path(
        os.getenv("API_BASE") or os.getenv("API_VERSION_BASE"), "/v1/api"
    )

    # Public mount prefix added by the reverse proxy. Example: /job-board-api.
    PUBLIC_URL_PREFIX = _normalize_prefix(os.getenv("PUBLIC_URL_PREFIX"))

    # Public Swagger basePath used by Swagger UI "Try it out" requests.
    # In production behind nginx this should usually be /job-board-api/v1/api.
    SWAGGER_BASE_PATH = _normalize_path(
        os.getenv("SWAGGER_BASE_PATH")
        or os.getenv("API_VERSION_BASE")
        or _join_url_paths(PUBLIC_URL_PREFIX, API_BASE),
        API_BASE,
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
