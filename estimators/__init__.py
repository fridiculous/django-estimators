from django.conf import settings
import os

ESTIMATOR_UPLOAD_DIR = getattr(settings, "ESTIMATOR_UPLOAD_DIR", 'estimators/')
FEATURE_MATRIX_DIR = getattr(settings, "FEATURE_MATRIX_DIR", 'feature_datasets/')
TARGET_VECTOR_DIR = getattr(settings, "TARGET_VECTOR_DIR", 'target_datasets/')


files_map = {
    'estimator': ESTIMATOR_UPLOAD_DIR,
    'FeatureMatrix': FEATURE_MATRIX_DIR,
    'TargetVector': TARGET_VECTOR_DIR,
}


def get_upload_path(instance, filename):
    directory = files_map.get(instance._object_property, '')
    full_path = os.path.join(directory, filename)
    return full_path
