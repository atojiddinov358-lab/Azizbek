import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def env_bool(name, default=False):
    return os.getenv(name, "1" if default else "0").lower() in ("1", "true", "yes")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-insecure-key")
DEBUG = env_bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]
if not DEBUG and SECRET_KEY == "dev-only-insecure-key":
    raise RuntimeError("Set DJANGO_SECRET_KEY (or set DJANGO_DEBUG=1 for local work).")

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "accounts", "archive", "premium", "core",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
if os.getenv("DB_NAME"):
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.postgresql", "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER", ""), "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"), "PORT": os.getenv("DB_PORT", "5432"),
    }}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"django.contrib.auth.password_validation.{n}"}
    for n in ("UserAttributeSimilarityValidator", "MinimumLengthValidator",
              "CommonPasswordValidator", "NumericPasswordValidator")
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# ---- Project ----
ACCESS_CODE_PEPPER = os.getenv("ACCESS_CODE_PEPPER", "dev-only-pepper")
PREMIUM_PRICE_USD = os.getenv("PREMIUM_PRICE_USD", "2.00")
PREMIUM_DURATION_DAYS = int(os.getenv("PREMIUM_DURATION_DAYS", "30"))
CODE_ATTEMPTS_PER_USER = 5   # per 10 minutes
CODE_ATTEMPTS_PER_IP = 20    # per hour

if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
LOGGING = {"version": 1, "disable_existing_loggers": False,
           "handlers": {"console": {"class": "logging.StreamHandler"}},
           "root": {"handlers": ["console"], "level": "INFO"}}
