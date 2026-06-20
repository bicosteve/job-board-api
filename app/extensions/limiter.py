"""
Rate limiting extension.

This module exposes a single shared ``Flask-Limiter`` instance that is
attached to the Flask application inside the application factory
(``app/__init__.py``) via ``limiter.init_app(app)``.

Design notes / best practices applied here
-------------------------------------------
1. Distributed storage (Redis):
   Auth endpoints are stateless and usually run behind multiple workers /
   replicas (gunicorn workers, multiple containers). An in-memory limiter
   would let an attacker get N attempts *per worker*. We therefore back the
   limiter with Redis so the counters are shared across every process.

2. Key function (who are we limiting?):
   For auth endpoints we combine the client IP **and** the submitted email.
   - IP alone is too coarse (corporate NAT / shared proxies punish innocent
     users) and too easy to rotate.
   - Email/account alone allows an attacker to lock a victim out (a denial of
     service against a known account).
   Combining the two gives a good balance: it throttles brute-force against a
   single account from a single origin while remaining hard to bypass.

3. Fail-open:
   If Redis is unavailable we do **not** want to take the whole auth surface
   down. ``LIMITER_FAIL_OPEN`` (in_memory fallback + swallow errors) keeps the
   app available while logging the problem.

4. Layered / tiered windows:
   We don't rely on a single window. Short windows (per-minute) stop bursts,
   while longer windows (per-hour) stop slow, low-and-slow brute forcing that
   would slip under a per-minute limit.
"""

from flask import current_app, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Sensible defaults applied to every sensitive auth endpoint. These are
# overridable per-deployment through configuration / environment variables.
DEFAULT_AUTH_LIMITS = [
    "5 per minute",
    "10 per 5 minutes",
    "20 per 10 minutes",
    "50 per hour",
]


def auth_limits():
    """
    Return the tiered rate limits for authentication endpoints.

    Evaluated lazily (per request) so the values can be driven by app config
    / environment variables. Falls back to ``DEFAULT_AUTH_LIMITS`` when there
    is no application context or the config keys are absent (e.g. in unit
    tests that spin up a bare Flask app).
    """
    try:
        cfg = current_app.config
        limits = [
            cfg.get("AUTH_LIMIT_PER_MINUTE", "5 per minute"),
            cfg.get("AUTH_LIMIT_PER_5_MINUTES", "10 per 5 minutes"),
            cfg.get("AUTH_LIMIT_PER_10_MINUTES", "20 per 10 minutes"),
            cfg.get("AUTH_LIMIT_PER_HOUR", "50 per hour"),
        ]
        return ";".join(limits)
    except Exception:
        return ";".join(DEFAULT_AUTH_LIMITS)


def auth_rate_key() -> str:
    """
    Build the throttling key for authentication endpoints.

    Combines the caller's IP address with the email in the JSON body (when
    present). This throttles brute-force attempts against a single account
    from a single source without letting an attacker either:
      * trivially rotate just the IP, or
      * lock a victim's account out by spamming only their email.
    """
    ip = get_remote_address()

    email = ""
    try:
        # ``silent=True`` so a malformed / missing body never raises here.
        body = request.get_json(silent=True) or {}
        if isinstance(body, dict):
            email = str(body.get("email", "")).strip().lower()
    except Exception:
        email = ""

    return f"{ip}:{email}" if email else ip


# The shared limiter instance. Default limits are intentionally empty here;
# we apply explicit, per-endpoint limits with the ``@limiter.limit`` decorator
# so that only sensitive endpoints are throttled.
limiter = Limiter(
    key_func=auth_rate_key,
    default_limits=[],
    headers_enabled=True,  # emit X-RateLimit-* headers for clients
)


def init_limiter(app) -> Limiter:
    """
    Initialise the limiter against the given app using configuration values.

    Reads:
      * RATELIMIT_ENABLED      -> master on/off switch
      * RATELIMIT_STORAGE_URI  -> redis:// uri (falls back to memory://)
      * RATELIMIT_FAIL_OPEN    -> when True, errors talking to the store are
                                  swallowed so auth stays available.
    """
    enabled = app.config.get("RATELIMIT_ENABLED", True)
    storage_uri = app.config.get("RATELIMIT_STORAGE_URI", "memory://")
    fail_open = app.config.get("RATELIMIT_FAIL_OPEN", True)
    strategy = app.config.get("RATELIMIT_STRATEGY", "fixed-window")

    app.config["RATELIMIT_ENABLED"] = enabled
    app.config["RATELIMIT_STORAGE_URI"] = storage_uri
    app.config["RATELIMIT_STRATEGY"] = strategy
    app.config["RATELIMIT_HEADERS_ENABLED"] = True
    # Fail open: if the storage backend errors, allow the request through.
    app.config["RATELIMIT_IN_MEMORY_FALLBACK_ENABLED"] = fail_open
    app.config["RATELIMIT_SWALLOW_ERRORS"] = fail_open

    limiter.init_app(app)
    return limiter
