from app import create_app

app = create_app()

print("CELERY_BROKER_URL:", app.config.get("CELERY_BROKER_URL"))
print("CELERY_RESULT_BACKEND:", app.config.get("CELERY_RESULT_BACKEND"))

if __name__ == "__main__":
    host = app.config["HOST"]
    port = int(app.config["PORT"])
    debug = app.config["DEBUG"]

    app.run(host=host, port=port)
