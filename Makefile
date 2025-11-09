ENV ?= dev

run:
	ENV=$(ENV) \
	FLASK_ENV=development \
	python run.py

test:
	python -m unittest discover -s tests

coverage:
	coverage run -m unittest discover -s tests

containers:
	ENV=docker \
	FLASK_ENV=development \
	docker compose up --build -d

container_logs:
	docker compose logs -f

stop:
	docker compose down -v
