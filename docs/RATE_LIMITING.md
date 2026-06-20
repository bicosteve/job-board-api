# Rate Limiting & Brute-Force Protection

This service throttles its **sensitive authentication endpoints** to slow down
credential-stuffing / brute-force attacks. It is implemented with
[`Flask-Limiter`](https://flask-limiter.readthedocs.io/) backed by **Redis**.

## What is protected

The following endpoints carry tiered rate limits:

| Endpoint                             | Method | Why                            |
| ------------------------------------ | ------ | ------------------------------ |
| `LoginUserController`                | POST   | password guessing              |
| `VerifyUserAccountController`        | POST   | OTP / verification brute-force |
| `RequestUserPasswordResetController` | POST   | reset-email flooding           |
| `ResetUserPasswordController`        | POST   | reset-token guessing           |
| `LoginAdminController`               | POST   | admin password guessing        |
| `VerifyAdminAccountController`       | POST   | admin OTP brute-force          |

Registration is intentionally **not** throttled the same way; add a limit there
too if you start seeing abuse.

## How it works

- Each protected `Resource` declares `decorators = [limiter.limit(auth_limits)]`.
  Using the `decorators` class attribute is the Flask-RESTful-friendly way to
  attach the limiter to every HTTP verb of the resource.
- `auth_limits()` returns the tiered limit string (read lazily from config), e.g.
  `"5 per minute;10 per 5 minutes;20 per 10 minutes;50 per hour"`.
- The limiter is initialised in the app factory via `init_limiter(app)`.

## Best practices applied

1. **Distributed storage (Redis).**
   Counters live in Redis so the limit is enforced _globally_ across every
   gunicorn worker and every container replica. An in-memory store would give an
   attacker `N attempts × number_of_workers`.

2. **Smart key function (IP + email).**
   We key on `client_ip:email`. IP-only punishes users behind shared NAT and is
   trivial to rotate; email-only lets an attacker lock a victim out. Combining
   both is the balanced choice. See `auth_rate_key()` in
   `app/extensions/limiter.py`.

3. **Tiered / layered windows.**
   A short window (per-minute) stops bursts; longer windows (per-hour) catch
   slow "low-and-slow" attacks that stay under the per-minute threshold.

4. **Fail-open.**
   If Redis is unreachable, `RATELIMIT_FAIL_OPEN=true` enables an in-memory
   fallback and swallows storage errors so a Redis outage never takes down login.

5. **Client feedback.**
   `X-RateLimit-*` headers are emitted and a `429 Too Many Requests` is returned
   once a limit is exceeded, so well-behaved clients can back off.

6. **Trust the right client IP.**
   When running behind a reverse proxy / load balancer (nginx, ALB, Cloudflare),
   make sure the app sees the real client IP via `X-Forwarded-For`. Configure
   `ProxyFix` (Werkzeug) so `get_remote_address()` is not just the proxy's IP.

## Configuration

All values are environment-driven (see `.env.example`):

| Variable                    | Default                | Purpose                         |
| --------------------------- | ---------------------- | ------------------------------- |
| `RATELIMIT_ENABLED`         | `true`                 | master on/off switch            |
| `RATELIMIT_FAIL_OPEN`       | `true`                 | allow requests if Redis is down |
| `RATELIMIT_STRATEGY`        | `fixed-window`         | counting strategy               |
| `RATELIMIT_STORAGE_URI`     | derived from `REDIS_*` | Redis connection for counters   |
| `AUTH_LIMIT_PER_MINUTE`     | `5 per minute`         | burst protection                |
| `AUTH_LIMIT_PER_5_MINUTES`  | `10 per 5 minutes`     | short-window protection         |
| `AUTH_LIMIT_PER_10_MINUTES` | `20 per 10 minutes`    | medium-window protection        |
| `AUTH_LIMIT_PER_HOUR`       | `50 per hour`          | slow brute-force protection     |

## Testing locally

```bash
# fire 10 quick logins and watch for 429s
for i in $(seq 1 10); do \
  curl -s -o /dev/null -w "%{http_code}\n" \
    -H 'Content-Type: application/json' \
    -d '{"email":"a@b.com","password":"x"}' \
    http://localhost:5005/v0/api/login; \
done
```

You should see `200/4xx` responses initially, then `429` once the per-minute
limit is exceeded.
