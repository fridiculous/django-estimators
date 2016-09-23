import os

from django.conf import settings
from django.db import models

from estimators import (ESTIMATOR_UPLOAD_DIR, FEATURE_MATRIX_DIR,
                        TARGET_VECTOR_DIR)


class AbstractPersistanceManager(models.Manager):

    def all_persisted_files(self, directory=None, relative_to_root=True, UPLOAD_DIR=''):
        if directory is None:
            directory = os.path.join(settings.MEDIA_ROOT, UPLOAD_DIR)
        all_files = []
        for root, dirs, files in os.walk(directory):
            for filename in files:
                rel_path = os.path.join(root, filename)
                if relative_to_root:
                    rel_path = os.path.relpath(
                        rel_path, start=settings.MEDIA_ROOT)
                all_files.append(rel_path)
        return all_files

    def unreferenced_files(self, directory=None):
        all_files = set(self.all_persisted_files(directory=directory))
        files_referenced = set(self.filter(
            object_file__in=all_files).values_list('object_file', flat=True))
        files_unreferenced = all_files - files_referenced
        return files_unreferenced

    def empty_records(self):
        all_files = self.all_persisted_files()
        empty_records = self.exclude(object_file__in=all_files).all()
        return empty_records


class EstimatorManager(AbstractPersistanceManager):

    def all_persisted_files(self, *args, **kwargs):
        return super().all_persisted_files(*args, **kwargs, UPLOAD_DIR=ESTIMATOR_UPLOAD_DIR)


class FeatureMatrixManager(AbstractPersistanceManager):

    def all_persisted_files(self, *args, **kwargs):
        return super().all_persisted_files(*args, **kwargs, UPLOAD_DIR=FEATURE_MATRIX_DIR)


class TargetManager(AbstractPersistanceManager):

    def all_persisted_files(self, *args, **kwargs):
        return super().all_persisted_files(*args, **kwargs, UPLOAD_DIR=TARGET_VECTOR_DIR)
