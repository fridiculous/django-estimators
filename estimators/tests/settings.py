SECRET_KEY = 'testing settings file'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'estimators',
)

DATABASE_ENGINE = 'sqlite3',
DATABASES = {
    'default': {
        'NAME': ':memory:',
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST_NAME': ':memory:',
    },
}
DATABASE_NAME = ':memory:'
TEST_DATABASE_NAME = ':memory:'

MIDDLEWARE_CLASSES = []

import tempfile
MEDIA_ROOT = tempfile.gettempdir()

DEBUG = True
