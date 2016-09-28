from django.conf import settings
import os

ESTIMATOR_DIR = getattr(settings, "ESTIMATOR_DIR", 'estimators/')
DATASET_DIR = getattr(settings, "DATASET_DIR", 'datasets/')

FEATURE_MATRIX_DIR = getattr(settings, "FEATURE_MATRIX_DIR", 'feature_datasets/')
TARGET_VECTOR_DIR = getattr(settings, "TARGET_VECTOR_DIR", 'target_datasets/')
PREDICTED_VECTOR_DIR = getattr(settings, "PREDICTED_VECTOR_DIR", 'predicted_datasets/')


files_map = {
    '_estimator': ESTIMATOR_DIR,
    '_data': DATASET_DIR,

    '_dataframe': FEATURE_MATRIX_DIR,
    '_array': TARGET_VECTOR_DIR,
    '_array': PREDICTED_VECTOR_DIR,
}


def get_upload_path(instance, filename):
    directory = files_map[instance._object_property]
    full_path = os.path.join(directory, filename)
    return full_path
