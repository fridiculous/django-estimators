# using test version of settings.py
# pytest_plugins = "estimators.tests.django",

import django
import os
#from estimators.tests import settings as test_settings


def pytest_report_header(config):
    return "Here comes the dynamite (boom)"


def pytest_configure(config):
    os.environ['DJANGO_SETTINGS_MODULE'] = "estimators.tests.settings"
    django.setup()
