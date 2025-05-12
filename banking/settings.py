from pathlib import Path
import os
from dotenv import load_dotenv

from utils.helpers import get_env_variable


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = get_env_variable("SECRET_KEY", "secretkey")

DEBUG = get_env_variable("DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # 3rd Party Apps
    # Local apps
    "app.apps.AppConfig",
    "users.apps.UsersConfig",
    "_user.apps.UserConfig",
    "_admin.apps.AdminConfig",
    "accounts.apps.AccountsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "banking.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "banking.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_env_variable("MYSQL_NAME", "mydatabase"),
        "USER": get_env_variable("MYSQL_USER", "myuser"),
        "PASSWORD": get_env_variable("MYSQL_PASSWORD", "mypassword"),
        "HOST": get_env_variable("MYSQL_HOST", "localhost"),
        "PORT": get_env_variable("MYSQL_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = get_env_variable("EMAIL_HOST_USER", "your-email@example.com")
EMAIL_HOST_PASSWORD = get_env_variable("EMAIL_HOST_PASSWORD", "your-email-password")

DEFAULT_FROM_EMAIL = get_env_variable("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

AUTH_USER_MODEL = "users.User"
