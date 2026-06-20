# Deploying a Dockerized Flask App to AWS EC2 with a Private Data Subnet

A practical walkthrough of deploying a Flask + Celery application using Docker on AWS EC2, with data services (MariaDB, Redis, RabbitMQ) isolated on a private subnet EC2 instance.

---

## Architecture

```
Internet
   │
   ▼
[Nginx :80]  ←── Public EC2 (10.0.1.x)
   │
   ▼
[Gunicorn :5005]  ←── Flask App Container
[Celery Worker]   ←── Celery Container
   │
   ▼ (VPC internal traffic only)
[Private EC2 (10.0.3.x)]
   ├── MariaDB  :3306
   ├── Redis    :6379
   └── RabbitMQ :5672
```

Two EC2 instances in the same VPC:

- **Public EC2** — runs the application containers, reachable from the internet
- **Private EC2** — runs data services, reachable only from within the VPC

---

## Part 1 — Prepare the Private EC2 (Data Services)

### 1.1 MariaDB

Verify MariaDB is listening on all interfaces:

```bash
sudo grep -rE "bind.address" /etc/my.cnf /etc/my.cnf.d/ 2>/dev/null
```

Edit the server config to disable hostname resolution and bind to all interfaces:

```bash
sudo nano /etc/my.cnf.d/mariadb-server.cnf
```

Add under `[mysqld]`:

```ini
[mysqld]
bind-address = 0.0.0.0
skip-name-resolve
```

Restart MariaDB:

```bash
sudo systemctl restart mariadb
sudo ss -tlnp | grep 3306
```

Create the application database and user:

```bash
sudo mysql -u root
```

```sql
CREATE DATABASE IF NOT EXISTS `job-board-api`;
CREATE USER 'dbusr'@'%' IDENTIFIED BY '***';
GRANT ALL PRIVILEGES ON `job-board-api`.* TO 'dbusr'@'%';
FLUSH PRIVILEGES;
SELECT user, host FROM mysql.user WHERE user = 'dbusr';
EXIT;
```

### 1.2 Redis

Edit the Redis config:

```bash
sudo nano /etc/redis/redis.conf
```

Set:

```
bind 0.0.0.0
requirepass ****
protected-mode no
```

Restart and verify:

```bash
sudo systemctl restart redis-server
redis-cli -a **** ping
```

### 1.3 RabbitMQ

Add the hostname to `/etc/hosts` so Erlang can resolve it:

```bash
echo "127.0.0.1 $(hostname -s)" | sudo tee -a /etc/hosts
```

Start and enable RabbitMQ:

```bash
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server
```

Use the correct `rabbitmqctl` binary (manual install):

```bash
~/rabbitmq_server-3.13.0/sbin/rabbitmqctl status
```

Create the application user:

```bash
~/rabbitmq_server-3.13.0/sbin/rabbitmqctl add_user dbusr ******
~/rabbitmq_server-3.13.0/sbin/rabbitmqctl set_user_tags dbusr administrator
~/rabbitmq_server-3.13.0/sbin/rabbitmqctl set_permissions -p / dbusr ".*" ".*" ".*"
~/rabbitmq_server-3.13.0/sbin/rabbitmqctl delete_user guest
~/rabbitmq_server-3.13.0/sbin/rabbitmqctl list_users
```

Add RabbitMQ to PATH permanently:

```bash
echo 'export PATH=$PATH:/home/ec2-user/rabbitmq_server-3.13.0/sbin' >> ~/.bashrc
source ~/.bashrc
```

---

## Part 2 — Security Groups

### Private EC2 — Inbound Rules

Open data service ports to the **public EC2's security group ID** only (not a CIDR range):

| Port | Protocol | Source                 | Purpose  |
| ---- | -------- | ---------------------- | -------- |
| 3306 | TCP      | sg-xxx (public EC2 SG) | MariaDB  |
| 6379 | TCP      | sg-xxx (public EC2 SG) | Redis    |
| 5672 | TCP      | sg-xxx (public EC2 SG) | RabbitMQ |
| 22   | TCP      | Bastion / SSM          | SSH      |

### Public EC2 — Inbound Rules

| Port | Protocol | Source    | Purpose      |
| ---- | -------- | --------- | ------------ |
| 22   | TCP      | Your IP   | SSH          |
| 80   | TCP      | 0.0.0.0/0 | HTTP (Nginx) |

---

## Part 3 — Prepare the Public EC2 (Application Server)

### 3.1 Install Docker

```bash
sudo dnf install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
newgrp docker
docker --version
```

### 3.2 Create the Production .env File

```bash
mkdir -p ~/job-board-api
nano ~/job-board-api/.env
```

```dotenv
# ===== Flask & App =====
ENV=prod
DEBUG=False
HOST=0.0.0.0
PORT=5005

# ===== Database (MySQL/MariaDB) =====
DB_HOST=<PRIVATE_EC2_IP>
DB_USER=dbusr
DB_PASSWORD=usr@123
DB_NAME=job-board-api
DB_PORT=3306

# ===== Redis =====
REDIS_HOST=<PRIVATE_EC2_IP>
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=usr@123

# ===== RabbitMQ =====
RABBITMQ_HOST=<PRIVATE_EC2_IP>
RABBITMQ_USER=
RABBITMQ_PASSWORD=
RABBITMQ_PORT=5672
RABBITMQ_VHOST=/

# ===== Celery =====
CELERY_BROKER_URL=amqp://dbusr:<password>@<PRIVATE_EC2_IP>:5672//
CELERY_RESULT_BACKEND=redis://:<password>@<PRIVATE_EC2_IP>:6379/0

# ===== JWT =====
JWT_SECRET=mysupersecret
JWT_ALGORITHM=HS256
JWT_TOKEN_EXPIRY_HOURS=48
```

> Replace `<PRIVATE_EC2_IP>` with the actual private IP of your data EC2 (e.g. `10.0.3.248`).
> Key difference from local `.env`: `HOST=0.0.0.0` (not `127.0.0.1`) so the container accepts external connections.

### 3.3 Verify Connectivity Before Deploying

```bash
PRIVATE_IP=<PRIVATE_EC2_IP>
nc -zv $PRIVATE_IP 3306   # MariaDB
nc -zv $PRIVATE_IP 6379   # Redis
nc -zv $PRIVATE_IP 5672   # RabbitMQ
```

All three should return `Connection succeeded`.

---

## Part 4 — Deploy the Application Containers

### 4.1 Pull the Image

```bash
docker pull bixoloo/job-board-api:latest
```

### 4.2 Run the Flask App

```bash
docker run -d \
  --name job-board-api \
  --env-file ~/job-board-api/.env \
  -p 5005:5005 \
  --restart unless-stopped \
  bixoloo/job-board-api:latest
```

### 4.3 Run the Celery Worker

Same image, different startup command:

```bash
docker run -d \
  --name job-board-celery \
  --env-file ~/job-board-api/.env \
  --restart unless-stopped \
  bixoloo/job-board-api:latest \
  celery -A celery_worker.celery worker --loglevel=info
```

### 4.4 Verify Both Containers

```bash
docker ps
docker logs --tail 50 job-board-api
docker logs --tail 50 job-board-celery
curl http://localhost:5005/v0/api/health/check
```

Healthy Celery output:

```
.> transport:   amqp://dbusr:**@10.0.3.248:5672//
.> results:     redis://10.0.3.248:6379/0
[INFO] Connected to amqp://dbusr:**@10.0.3.248:5672//
[INFO] celery@<container-id> ready.
```

### 4.5 Update / Redeploy Command

```bash
docker stop job-board-api job-board-celery && \
docker rm job-board-api job-board-celery && \
docker pull bixoloo/job-board-api:latest && \
docker run -d --name job-board-api --env-file ~/job-board-api/.env \
  -p 5005:5005 --restart unless-stopped bixoloo/job-board-api:latest && \
docker run -d --name job-board-celery --env-file ~/job-board-api/.env \
  --restart unless-stopped bixoloo/job-board-api:latest \
  celery -A celery_worker.celery worker --loglevel=info
```

---

## Part 5 — Nginx Reverse Proxy

Install and configure Nginx to serve the app on port 80:

```bash
sudo dnf install -y nginx
```

Create the site config:

```bash
sudo tee /etc/nginx/conf.d/job-board-api.conf << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass         http://127.0.0.1:5005;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        proxy_read_timeout 90;
    }
}
EOF
```

Enable and start:

```bash
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl start nginx
```

Test via public IP:

```bash
curl http://<PUBLIC_EC2_IP>/v0/api/health/check
```

---

## Part 6 — Swagger API Documentation

The Swagger UI is mounted by Flasgger at `/apidocs/` — independent of the `API_VERSION_BASE` prefix used by application routes:

```
http://<PUBLIC_EC2_IP>/apidocs/
```

| URL Pattern                       | Purpose               |
| --------------------------------- | --------------------- |
| `http://<IP>/v0/api/health/check` | Health check endpoint |
| `http://<IP>/v0/api/...`          | Application routes    |
| `http://<IP>/apidocs/`            | Swagger UI            |

> Nginx proxies all paths transparently to Gunicorn. The `/apidocs/` path is registered directly by the Swagger library (Flasgger), not by your application router, which is why it sits outside the `/v0/api/` prefix.

---

## Key Lessons

- `HOST=0.0.0.0` is required in Docker — `127.0.0.1` is the container's own loopback and unreachable from outside
- Use the **Security Group ID** as the inbound source on the private EC2, not a CIDR — this restricts access to only your public EC2
- `skip-name-resolve` in MariaDB prevents hostname resolution failures across VPC subnets
- MariaDB user must be created with `'user'@'%'` not `'user'@'localhost'` for remote connections
- RabbitMQ's Erlang cookie must match between the server process and the CLI tool
- Celery and Flask can run from the same Docker image using different startup commands
- Celery ignores Flask app config if the `Celery()` instance is created before `create_app()` — pass `CELERY_BROKER_URL` directly as an env var to work around this
- Swagger UI (`http://ec2-3-69-30-108.eu-central-1.compute.amazonaws.com/apidocs/#/`) is mounted by the library itself and does not inherit the app's URL base prefix
  RY_BROKER_URL` directly as an env var to work around this
- Swagger UI (`http://ec2-3-69-30-108.eu-central-1.compute.amazonaws.com/apidocs/#/`) is mounted by the library itself and does not inherit the app's URL base prefix
