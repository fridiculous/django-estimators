import shutil
import os

from django.apps import apps
from django.db import models
from django.conf import settings
from estimators import ESTIMATOR_UPLOAD_DIR


class EstimatorManager(models.Manager):

    def all_persisted_files(self, directory=None, relative_to_root=True):
        if directory is None:
            directory = os.path.join(settings.MEDIA_ROOT, ESTIMATOR_UPLOAD_DIR)
        all_files = []
        for root, dirs, files in os.walk(directory):
            for filename in files:
                rel_path = os.path.join(root, filename)
                if relative_to_root:
                    rel_path = os.path.relpath(rel_path, start=settings.MEDIA_ROOT)
                all_files.append(rel_path)
        return all_files

    def unreferenced_files(self, directory=None):
        all_files = set(self.all_persisted_files(directory=directory))
        files_referenced = set(self.filter(estimator_file__in=all_files).values_list('estimator_file', flat=True))
        files_unreferenced = all_files - files_referenced
        return files_unreferenced

    def empty_records(self):
        all_files = self.all_persisted_files()
        empty_records = self.exclude(estimator_file__in=all_files).all()
        return empty_records
