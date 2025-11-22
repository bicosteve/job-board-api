run:
	python run.py

test:
	python -m unittest discover -s tests

coverage:
	coverage run -m unittest discover -s tests

containers:
	docker compose --env-file .env.docker up --build -d

container_logs:
	docker compose logs -f

stop:
	docker compose down -v
