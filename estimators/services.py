import shutil
import os

from .models import Estimator
from django.apps import apps
from django.conf import settings


class EstimatorManager():

    @classmethod
    def _get_all_files(cls, directory=None, relative_to_root=True):
        if directory is None:
            directory = os.path.join(settings.MEDIA_ROOT, settings.ESTIMATOR_UPLOAD_DIR)
        all_files = []
        for root, dirs, files in os.walk(directory):
            for filename in files:
                rel_path = os.path.join(root, filename)
                if relative_to_root:
                    rel_path = os.path.relpath(rel_path, start=settings.MEDIA_ROOT)
                all_files.append(rel_path)
        return all_files

    @classmethod
    def _get_unreferenced_files(cls, directory=None):
        all_files = set(cls._get_all_files(directory=directory))
        files_referenced = set(Estimator.objects.filter(estimator_file__in=all_files).values_list('estimator_file', flat=True))
        files_unreferenced = all_files - files_referenced
        return files_unreferenced

    @classmethod
    def _get_empty_records(cls):
        all_files = cls._get_all_files()
        empty_records = Estimator.objects.exclude(estimator_file__in=all_files).all()
        return empty_records

    @classmethod
    def delete_empty_records(cls):
        empty_records = cls._get_empty_records()
        return empty_records.delete()

    @classmethod
    def delete_unreferenced_files(cls):
        unreferenced_files = cls._get_unreferenced_files()
        for unreferenced_path in unreferenced_files:
            os.remove(os.path.join(settings.MEDIA_ROOT, unreferenced_path))
        return len(unreferenced_files)

    @classmethod
    def load_unreferenced_files(cls, directory=None):
        unreferenced_files = cls._get_unreferenced_files(directory=directory)
        for filename in unreferenced_files:
            m = Estimator.create_from_file(filename)
            try:
                m.save()
            except:
                pass
        return len(unreferenced_files)
