"""
Django settings for ethiopia_imports project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ===== SECURITY =====
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-your-secret-key-here-change-this-in-production')
DEBUG = os.getenv('DEBUG', 'False') == 'True'  # Changed to False by default

# ===== ALLOWED HOSTS =====
# Update this with your actual domain
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'Chacha19.pythonanywhere.com',  # Replace with your PythonAnywhere username
    '.pythonanywhere.com',  # Allows any subdomain
]

# ===== INSTALLED APPS =====
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'products',
    'accounts',
    'django_filters',
    'crispy_forms',
    'crispy_tailwind',
]

# ===== MIDDLEWARE =====
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ADD THIS for static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ethiopia_imports.urls'

# ===== TEMPLATES =====
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'products.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'ethiopia_imports.wsgi.application'

# ===== DATABASE =====
# SQLite is fine for PythonAnywhere free tier
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ===== AUTH =====
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===== INTERNATIONALIZATION =====
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Addis_Ababa'
USE_I18N = True
USE_TZ = True

# ===== STATIC & MEDIA FILES =====
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # PythonAnywhere expects this
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# WhiteNoise for static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ===== DEFAULT =====
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===== CRISPY FORMS =====
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

# ===== WHATSAPP & TELEGRAM =====
WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER', '+251913605252')
TELEGRAM_USERNAME = os.getenv('TELEGRAM_USERNAME', 'your_username')

# ===== AUTHENTICATION =====
LOGIN_REDIRECT_URL = '/products/'
LOGOUT_REDIRECT_URL = '/products/'
LOGIN_URL = '/accounts/login/'

# ===== LOGGING =====
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}