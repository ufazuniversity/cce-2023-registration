"""
Django settings for cce_2023_registration project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path

import dj_database_url
from decouple import Csv
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
PROJECT_DIR = Path(__file__).resolve().parent
BASE_DIR = PROJECT_DIR.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool, default=False)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default="")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
    "django_extensions",
    "phonenumber_field",
    "ckeditor",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "core",
    "solo",
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = "cce_2023_registration.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [PROJECT_DIR / "templates"],
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

WSGI_APPLICATION = "cce_2023_registration.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASE_URL = config("DATABASE_URL", default="sqlite:///db.sqlite3")

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Baku"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "static"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Phone-number-field settings
PHONENUMBER_DEFAULT_REGION = config("PHONENUMBER_DEFAULT_REGION", "AZ")

# Custom form renderer
FORM_RENDERER = "core.renderers.BootstrapFormRenderer"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

LOGIN_REDIRECT_URL = "index"

SITE_ID = 1

# Django allauth configs
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_SESSION_REMEMBER = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_MAX_EMAIL_ADDRESSES = 1
ACCOUNT_FORMS = {
    "signup": "core.forms.SignupForm",
    "login": "core.forms.LoginForm",
    "reset_password": "core.forms.ResetPasswordForm",
    "reset_password_from_key": "core.forms.ResetPasswordKeyFrom",
    "set_password": "core.forms.SetPasswordForm",
    "change_password": "core.forms.ChangePasswordForm",
    "add_email": "core.forms.AddEmailForm",
}

# Email setup
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")

CONTACT_EMAIL = config("CONTACT_EMAIL")
CONTACT_PHONE = config("CONTACT_PHONE")

NOTICE_MESSAGE = (
    "Due to technical issues we are not able to accept payments at the moment. You can register and "
    "order tickets now and pay later. We will inform you when the payment is available."
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": config("DJANGO_LOG_LEVEL", default="INFO"),
        "propagate": False,
    },
}

CURRENCY = "AZN"

USE_S3 = config("USE_S3", cast=bool, default=False)
if USE_S3:
    DEFAULT_FILE_STORAGE = "cce_2023_registration.storage.MediaRootS3Boto3Storage"
    STATICFILES_STORAGE = "cce_2023_registration.storage.StaticRootS3Boto3Storage"
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME")
    AWS_S3_ENDPOINT_URL = f"https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com"
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
        "ACL": "public-read",
    }
    AWS_S3_CUSTOM_DOMAIN = f"ufaz-assets.ams3.cdn.digitaloceanspaces.com"
    AWS_IS_GZIPPED = True
    AWS_LOCATION = config("AWS_LOCATION")
    AWS_STATIC_LOCATION = f"{AWS_LOCATION}/static"
    AWS_MEDIA_LOCATION = f"{AWS_LOCATION}/media"


CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", cast=Csv(), default="")

# KapitalBank Ecommerce settings
KB_ECOMM_URL = config("KB_ECOMM_URL")
KB_ECOMM_MERCHANT_ID = config("KB_ECOMM_MERCHANT_ID")
KB_ECOMM_CURRENCY = config("KB_ECOMM_CURRENCY")
KB_ECOMM_ORDER_DESCRIPTION = config("KB_ECOMM_ORDER_DESCRIPTION")
KB_ECOMM_ORDER_APPROVE_URL = config("KB_ECOMM_ORDER_APPROVE_URL")
KB_ECOMM_ORDER_DECLINE_URL = config("KB_ECOMM_ORDER_DECLINE_URL")
KB_ECOMM_ORDER_CANCEL_URL = config("KB_ECOMM_ORDER_CANCEL_URL")
KB_ECOMM_CERT_PATH = config("KB_ECOMM_CERT_PATH")
KB_ECOMM_CERT_KEY_PATH = config("KB_ECOMM_CERT_KEY_PATH")