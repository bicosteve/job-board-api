from app import create_app
from app.extensions.celery import celery  # noqa: F401

flask_app = create_app()

__all__ = ["celery", "flask_app"]
