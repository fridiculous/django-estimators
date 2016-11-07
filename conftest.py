import django
import os


def pytest_report_header(config):
    return "Here comes the dynamite (boom)"


def pytest_configure(config):
    # using test version of settings.py
    os.environ['DJANGO_SETTINGS_MODULE'] = "estimators.tests.settings"
    django.setup()
