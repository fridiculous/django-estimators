SECRET_KEY = 'template settings file'

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
        'NAME': 'db.sqlite3',
        'ENGINE': 'django.db.backends.sqlite3',
    },
}

MIDDLEWARE_CLASSES = []

MEDIA_ROOT = 'files'

ESTIMATOR_DIR = 'estimators/'
DATASET_DIR = 'datasets/'

DEBUG = True
