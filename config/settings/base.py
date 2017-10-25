"""
Django settings for hasker project.
"""

import json
from os.path import abspath, dirname, join

from django.core.exceptions import ImproperlyConfigured


def root(*dirs):
    basedir = join(dirname(abspath(__file__)), '..', '..')
    return join(basedir, *dirs)


with open(root('secrets.json')) as _fd:
    _secrets = json.loads(_fd.read())


def get_secret(name):
    try:
        return _secrets[name]
    except KeyError:
        errmsg = 'Set the {0} environment variable.'.format(name)
        raise ImproperlyConfigured(errmsg)


BASE_DIR = root()

SECRET_KEY = get_secret('dj_secret_key')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.apps.CoreConfig',
    'hasker.apps.HaskerConfig',
    'rest_framework',
    'rest_framework_swagger',
    'api.apps.ApiConfig'
]

# Custom User's model
AUTH_USER_MODEL = 'core.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [root('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'hasker.context_processors.trending'
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Password validation

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


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_secret('db_name'),
        'USER': get_secret('db_user'),
        'PASSWORD': get_secret('db_pass'),
        'HOST': get_secret('db_host'),
        'PORT': get_secret('db_port'),
    }
}


# Static files (CSS, JavaScript, Images)

STATICFILES_DIRS = [root('static')]
STATIC_URL = '/static/'
MEDIA_ROOT = root('media')
MEDIA_URL = '/media/'


# SMTP
EMAIL_HOST = get_secret('smtp_host')
EMAIL_PORT = get_secret('smtp_port')
EMAIL_HOST_USER = get_secret('smtp_login')
EMAIL_HOST_PASSWORD = get_secret('smtp_password')
EMAIL_USE_TLS = get_secret('smtp_tls')
EMAIL_USE_SSL = get_secret('smtp_ssl')


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# REST framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/minute',
        'user': '60/minute'
    },
    'PAGE_SIZE': 10
}
