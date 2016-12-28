import django
import os
import tempfile

temp_dir = tempfile.TemporaryDirectory()


def pytest_configure(config):
    # using test version of settings.py
    os.environ['DJANGO_SETTINGS_MODULE'] = "estimators.tests.settings"
    django.setup()

    # set MEDIA_ROOT to temp_dir before starting tests
    from django.conf import settings
    settings.MEDIA_ROOT = temp_dir.name

def pytest_report_header(config):
    print('MEDIA_ROOT temporary directory: %s' % temp_dir.name)


def pytest_unconfigure(config):
    # remove temp_dir
    temp_dir.cleanup()
