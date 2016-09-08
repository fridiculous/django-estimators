import shutil
import os

from .models import MLModel
from django.apps import apps
from django.conf import settings


class MLModelManager():

    @classmethod
    def _get_all_files(cls, relative=True):
        directory = os.path.join(settings.MEDIA_ROOT, settings.MODELS_UPLOAD_DIR)
        all_files = []
        for root, dirs, files in os.walk(directory):
            for filename in files:
                rel_path = os.path.join(root, filename)
                if relative:
                    rel_path = os.path.relpath(rel_path, start=settings.MEDIA_ROOT)
                all_files.append(rel_path)
        return all_files

    @classmethod
    def _get_unreferenced_files(cls):
        all_files = set(cls._get_all_files())
        files_referenced = set(MLModel.objects.filter(model_file__in=all_files).values_list('model_file', flat=True))
        files_unreferenced = all_files - files_referenced
        return files_unreferenced

    @classmethod
    def _get_empty_ml_models(cls):
        all_files = cls._get_all_files()
        empty_ml_models = MLModel.objects.exclude(model_file__in=all_files).all()
        return empty_ml_models

    @classmethod
    def delete_empty_records(cls):
        empty_models = cls._get_empty_ml_models()
        return empty_models.delete()

    @classmethod
    def delete_unreferenced_files(cls):
        unreferenced_files = cls._get_unreferenced_files()
        for unreferenced_path in unreferenced_files:
            os.remove(os.path.join(settings.MEDIA_ROOT, unreferenced_path))
        return len(unreferenced_files)

    @classmethod
    def load_unreferenced_files(cls):
        unreferenced_files = cls._get_unreferenced_files()
        for filename in unreferenced_files:
            m = MLModel.create_from_file(filename)
            m.save()
        return len(unreferenced_files)
