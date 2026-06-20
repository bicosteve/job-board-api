# ====== App =====

install:
	pipenv install -r requirements.txt

activate:
	pipenv shell

run:
	python run.py

# ====== Background Worker =====
celery:
	celery -A celery_worker.celery worker --loglevel=info

# ====== Tests =====
test:
	python -m unittest discover -s tests

coverage:
	coverage run -m unittest discover -s tests -t .

report:
	coverage report -m


# ====== Docker =====
containers:
	docker compose --env-file .env.docker up --build -d

container_logs:
	docker compose logs -f

stop:
	docker compose down -v


# ====== Terraform =====
format:
	cd deployments && terraform fmt

init:
	cd deployments && terraform init

plan:
	cd deployments && terraform plan

apply:
	cd deployments && terraform apply


# ====== AWS Connect =====
connect-private:
	ssh -i node-01-KP.pem ec2-user@10.0.3.84

connect-public:
	ssh -i node-01-KP.pem ec2-user@3.69.30.108

