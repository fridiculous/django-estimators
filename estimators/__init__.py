from django.conf import settings

ESTIMATOR_UPLOAD_DIR = getattr(settings, "ESTIMATOR_UPLOAD_DIR", 'estimators/')
