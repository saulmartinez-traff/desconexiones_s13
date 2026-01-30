"""
Django settings for desconexiones_s13 project.
Production-ready configuration with environment-based settings.
"""

import os
from pathlib import Path
from datetime import timedelta

# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(os.path.join(BASE_DIR, 'backend', '.env'))

DEBUG = os.getenv('DEBUG', 'True') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ============================================================================
# INSTALLED APPLICATIONS
# ============================================================================
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',

    # Local apps
    'apps.organization',
    'apps.vehicles',
    'apps.registers',
    # 'apps.auth',
]

# ============================================================================
# CUSTOM USER MODEL
# ============================================================================
AUTH_USER_MODEL = 'organization.User'

# ============================================================================
# MIDDLEWARE
# ============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.error_handler.ErrorHandlerMiddleware',
    'middleware.logging.LoggingMiddleware',
]

ROOT_URLCONF = 'core.urls'

# ============================================================================
# TEMPLATES
# ============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
# Detectar si usar MySQL (desarrollo) o PostgreSQL (producción)
DB_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.mysql')

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': os.getenv('DB_NAME', 'desconexiones_s13'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306' if 'mysql' in DB_ENGINE else '5432'),
        'CHARSET': 'utf8mb4' if 'mysql' in DB_ENGINE else None,
        'COLLATION': 'utf8mb4_unicode_ci' if 'mysql' in DB_ENGINE else None,
    }
}

# ============================================================================
# AUTHENTICATION & PASSWORD VALIDATION
# ============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================================
# INTERNATIONALIZATION
# ============================================================================
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# ============================================================================
# STATIC & MEDIA FILES
# ============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================================
# DEFAULT PRIMARY KEY
# ============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# DJANGO REST FRAMEWORK CONFIGURATION
# ============================================================================
REST_FRAMEWORK = {
    # Authentication
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    # Permissions
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),

    # Filtering
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),

    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': int(os.getenv('REST_FRAMEWORK_DEFAULT_PAGINATION_SIZE', 20)),

    # Default renderer
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),

    # Throttling
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# ============================================================================
# JWT CONFIGURATION
# ============================================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JTI_CLAIM': 'jti',
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'AUTH_REFRESH_CLASSES': ('rest_framework_simplejwt.tokens.RefreshToken',),
}

# ============================================================================
# CORS CONFIGURATION
# ============================================================================
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',  # Vite default port
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
]

CORS_ALLOW_CREDENTIALS = True

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'error.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'services': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        }
    },
}

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================
# Telemetry API Configuration
TELEMETRY_API_URL = os.getenv('TELEMETRY_API_URL', '')
# TELEMETRY_API_KEY = os.getenv('TELEMETRY_API_KEY', '')

# VIN Filter (Global Filter)
VIN_FILTER_PATTERN = 'SZ'

# Geofence Settings
GEOFENCE_PRECISION = 6  # Decimal places for coordinates

# ETL Settings
ETL_BATCH_SIZE = 2000
ETL_PAGE_SIZE = 5000
ETL_TIMEOUT = 300  # seconds

# Security Settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
