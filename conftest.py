import django
import os
import shutil


def pytest_report_header(config):
    return "Here comes the dynamite (boom)"


def pytest_configure(config):
    # using test version of settings.py
    os.environ['DJANGO_SETTINGS_MODULE'] = "estimators.tests.settings"
    django.setup()


def pytest_unconfigure(config):
    """Remove tmp directory for testings"""
    from estimators.tests import settings
    shutil.rmtree(settings.MEDIA_ROOT)
