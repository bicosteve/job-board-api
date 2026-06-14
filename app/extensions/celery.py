from celery import Celery

celery = Celery(__name__)
flask_app = None  # will be populated by create_app()
