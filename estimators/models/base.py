import os

import dill

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from estimators import get_upload_path, hashing


class AbstractPersistObject(models.Model):

    create_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    object_hash = models.CharField(
        max_length=64, unique=True, default=None, null=False, editable=False)
    object_file = models.FileField(
        upload_to=get_upload_path, default=None, null=False, blank=True, editable=False)

    _object_arg_name = NotImplementedError()
    _object_property_name = NotImplementedError()

    class Meta:
        abstract = True

    @property
    def is_persisted(self):
        return self.object_file.name is not None and os.path.isfile(
            self.object_file.path)

    @classmethod
    def _compute_hash(cls, obj):
        return hashing.hash(obj)

    @classmethod
    def get_by_hash(cls, object_hash):
        query_set = cls.objects.filter(object_hash=object_hash)
        return query_set.first()

    @property
    def object_property(self):
        return getattr(self, self._object_property_name)

    @object_property.setter
    def object_property(self, obj):
        return setattr(self, self._object_property_name, obj)

    def get_object(self):
        if self.object_property is None:
            self.load()
        return self.object_property

    def set_object(self, value):
        object_hash = self._compute_hash(value)
        self.object_property = value
        self.object_hash = object_hash
        self.object_file.name = self.object_hash

    def persist(self):
        """a private method that persists an estimator object to the filesystem"""
        if self.object_hash:
            data = dill.dumps(self.object_property)
            f = ContentFile(data)
            self.object_file.save(self.object_hash, f)
            f.close()
            return True
        return False

    def load(self):
        """a private method that loads an estimator object from the filesystem"""
        if self.is_persisted:
            self.object_file.open()
            temp = dill.loads(self.object_file.read())
            self.set_object(temp)
            self.object_file.close()

    def save(self, *args, **kwargs):
        if not self.is_persisted:
            self.persist()
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create(cls, obj):
        """Returns an existing Estimator instance if found, otherwise creates a new Estimator.

        The recommended constructor for Estimators."""
        object_hash = cls._compute_hash(obj)
        # instance = cls.get_by_hash(object_hash)
        try:
            instance = cls.objects.get(object_hash=object_hash)
        except getattr(cls, "DoesNotExist"):
            # create object
            instance = cls()
            instance.set_object(obj)
            instance.save()
        return instance

    @classmethod
    def create_from_file(cls, filename):
        """Return an Estimator object given the path of the file, relative to the MEDIA_ROOT"""
        obj = cls()
        obj.object_file = filename
        obj.load()
        return obj

    @classmethod
    def delete_empty_records(cls):
        empty_records = cls.objects.empty_records()
        return empty_records.delete()

    @classmethod
    def delete_unreferenced_files(cls):
        unreferenced_files = cls.objects.unreferenced_files()
        for unreferenced_path in unreferenced_files:
            os.remove(os.path.join(settings.MEDIA_ROOT, unreferenced_path))
        return len(unreferenced_files)

    @classmethod
    def delete_duplicated_files(cls):
        duplicated_files = cls.objects.all_duplicated_files()
        for duplicated_path in duplicated_files:
            os.remove(os.path.join(settings.MEDIA_ROOT, duplicated_path))
        return len(duplicated_files)

    @classmethod
    def load_unreferenced_files(cls, directory=None):
        unreferenced_files = cls.objects.unreferenced_files(
            directory=directory)
        for filename in unreferenced_files:
            obj = cls.create_from_file(filename)
            obj.save()
        return len(unreferenced_files)
