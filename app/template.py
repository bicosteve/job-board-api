import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


def _clean_base_path(path: str) -> str:
    """Return a normalized Swagger/OpenAPI basePath value."""
    path = (path or "/v1/api").strip()
    if not path.startswith("/"):
        path = f"/{path}"
    return path.rstrip("/") or "/"


def get_swagger_host_and_schemes():
    env = os.getenv("ENV", "dev").lower()
    render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    server_host = os.getenv("SERVER_HOST")

    if env == "dev":
        return os.getenv("SWAGGER_HOST", "127.0.0.1:5005"), ["http"]
    if env == "prod":
        return os.getenv("SWAGGER_HOST", server_host), ["http"]
    return os.getenv("SWAGGER_HOST", render_host), ["https"]


SWAGGER_HOST, SWAGGER_SCHEMES = get_swagger_host_and_schemes()

swagger_template = {
    "info": {
        "title": "Job Board API",
        "description": "Job Board API Documentation",
        "version": os.getenv("API_VERSION", "1.0.0"),
        "contact": {
            "name": os.getenv("CONTACT_NAME", "Bico Oloo"),
            "email": os.getenv("CONTACT_EMAIL", "devbico@gmail.com"),
        },
    },
    "basePath": _clean_base_path(
        os.getenv("SWAGGER_BASE_PATH")
        or os.getenv("API_VERSION_BASE")
        or os.getenv("API_BASE")
        or "/v1/api"
    ),
    "host": SWAGGER_HOST,
    "schemes": SWAGGER_SCHEMES,
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT auth for Bearer scheme. e.g: `Bearer {token}`",
        }
    },
}
