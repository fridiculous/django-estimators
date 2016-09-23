import os
from itertools import chain

from django.conf import settings
from django.db import models
from estimators import (ESTIMATOR_DIR, FEATURE_MATRIX_DIR,
                        PREDICTED_VECTOR_DIR, TARGET_VECTOR_DIR)


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

    def group_persisted_files_by_hash(self):
        file_hash_groups = {}
        for f in self.all_persisted_files():
            file_hash = f.split('/')[-1].split('_')[0]
            if not file_hash_groups.get(file_hash):
                file_hash_groups[file_hash] = [f]
            else:
                file_hash_groups[file_hash].append(f)
        return file_hash_groups

    def all_duplicated_files(self):
        return list(chain.from_iterable([i[1:] for i in self.group_persisted_files_by_hash().values()]))

    def all_unique_files(self):
        return [i[0] for i in self.group_persisted_files_by_hash().values()]

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
        return super().all_persisted_files(*args, UPLOAD_DIR=ESTIMATOR_DIR, **kwargs)


class FeatureMatrixManager(AbstractPersistanceManager):

    def all_persisted_files(self, *args, **kwargs):
        return super().all_persisted_files(*args, UPLOAD_DIR=FEATURE_MATRIX_DIR, **kwargs)


class TargetManager(AbstractPersistanceManager):

    def all_persisted_files(self, *args, **kwargs):
        return super().all_persisted_files(*args, UPLOAD_DIR=TARGET_VECTOR_DIR, **kwargs)


class PredictedManager(AbstractPersistanceManager):

    def all_persisted_files(self, *args, **kwargs):
        return super().all_persisted_files(*args, UPLOAD_DIR=PREDICTED_VECTOR_DIR, **kwargs)
