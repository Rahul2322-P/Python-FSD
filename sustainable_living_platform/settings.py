from pathlib import Path
import os
import tempfile
import dj_database_url

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / '.env')
except ImportError:
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'v_r8k#68*9k22s*re#v1@v!m^*b^z@v^n*s@j*@o*m^d@z*z*i')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['.vercel.app', 'localhost', '127.0.0.1', '*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sustainable_living_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sustainable_living_platform.wsgi.application'

# Database configuration - PostgreSQL if configured, otherwise SQLite.
if os.environ.get('DATABASE_URL'):
    # Production environment with a full database URL
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
else:
    POSTGRES_ENABLED = os.environ.get('USE_POSTGRES', 'False').lower() in ('1', 'true', 'yes')
    POSTGRES_DB = os.environ.get('DB_NAME')
    POSTGRES_USER = os.environ.get('DB_USER')
    POSTGRES_PASSWORD = os.environ.get('DB_PASSWORD')
    POSTGRES_HOST = os.environ.get('DB_HOST', 'localhost')
    POSTGRES_PORT = os.environ.get('DB_PORT', '5432')

    if POSTGRES_ENABLED or (POSTGRES_DB and POSTGRES_USER and POSTGRES_PASSWORD):
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': POSTGRES_DB or 'ecolearn',
                'USER': POSTGRES_USER or 'postgres',
                'PASSWORD': POSTGRES_PASSWORD or '1234',
                'HOST': POSTGRES_HOST,
                'PORT': POSTGRES_PORT,
            }
        }
    else:
        # Local development and serverless runtime fallback
        if os.environ.get('VERCEL') == '1':
            sqlite_path = Path(tempfile.gettempdir()) / 'db.sqlite3'
        else:
            sqlite_path = BASE_DIR / 'db.sqlite3'

        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': sqlite_path,
            }
        }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'

# Email settings for OTP verification
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'no-reply@ecolearn.app')
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

# Admin secret code for secure admin login
ADMIN_SECRET_CODE = os.environ.get('ADMIN_SECRET_CODE', 'HONEY')
