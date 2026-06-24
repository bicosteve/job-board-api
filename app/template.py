import os

from dotenv import load_dotenv

load_dotenv()


def get_swagger_host_and_schemes():
    env = os.getenv("ENV")
    render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    server_host = os.getenv("SERVER_HOST")
    if env == "dev":
        return "127.0.0.1:5005", ["http"]
    elif env == "prod":
        return server_host, ["http"]
    else:
        return render_host, ["https"]


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
    "basePath": "/job-board-api/v1/api",
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
