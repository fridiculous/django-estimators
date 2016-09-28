import os

import dill

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
# original based on sci-kit hashing function
from estimators import get_upload_path, hashing
from estimators.managers import EstimatorManager


class AbstractPersistObject(models.Model):

    create_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    object_hash = models.CharField(max_length=64, unique=True, default=None, null=False, editable=False)
    object_file = models.FileField(upload_to=get_upload_path, default=None, null=False, blank=True, editable=False)

    _object_property = 'abstract_object'

    class Meta:
        abstract = True

    @property
    def is_persisted(self):
        return self.object_file.name is not None and os.path.isfile(self.object_file.path)

    @classmethod
    def _compute_hash(cls, obj):
        return hashing.hash(obj)

    @classmethod
    def get_by_hash(cls, object_hash):
        query_set = cls.objects.filter(object_hash=object_hash)
        return query_set.first()

    def get_abstract_object(self):
        return getattr(self, self._object_property)

    def set_abstract_object(self, obj):
        return setattr(self, self._object_property, obj)

    def get_object_as_property(self):
        if self.get_abstract_object() is None:
            self.load()
        return self.get_abstract_object()

    def set_object_property(self, value):
        object_hash = self._compute_hash(value)
        self.set_abstract_object(value)
        self.object_hash = object_hash
        self.object_file.name = self.object_hash

    def persist(self):
        """a private method that persists an estimator object to the filesystem"""
        if self.object_hash:
            data = dill.dumps(self.get_abstract_object())
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
            self.set_object_property(temp)
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
        instance = cls.get_by_hash(object_hash)
        if not instance:
            # create object
            instance = cls()
            instance.set_object_property(obj)
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
        unreferenced_files = cls.objects.unreferenced_files(directory=directory)
        for filename in unreferenced_files:
            obj = cls.create_from_file(filename)
            obj.save()
        return len(unreferenced_files)


class Estimator(AbstractPersistObject):

    """This class creates estimator objects that persists predictive models

        An Estimator instance has multiple attributes

            :description:
            :estimator:

            >>> from estimators.models import Estimator
            >>> est = Estimator()
            >>> est.estimator = object
            >>> est.description = "k-means with 5 clusters"
            >>> est.save()

        or

            >>> from estimators.models import Estimator
            >>> est = Estimator.get_or_create(object)
            >>> est.description = "kNN without parameter tuning"
            >>> est.save()
    """

    description = models.CharField(max_length=256)
    _estimator = None
    # required by base class, to refer to the estimator property
    _object_property = '_estimator'

    objects = EstimatorManager()

    class Meta:
        db_table = 'estimators'

    def __repr__(self):
        return '<Estimator <Id %s> <Hash %s>: %s>' % (self.id, self.object_hash, self.estimator)

    @classmethod
    def get_by_estimator(cls, est):
        if est is not None:
            object_hash = cls._compute_hash(est)
        return cls.get_by_hash(object_hash)

    @property
    def estimator(self):
        """return the estimator, and load it into memory if it hasn't been loaded yet"""
        return self.get_object_as_property()

    @estimator.setter
    def estimator(self, obj):
        self.set_object_property(obj)

    def save(self, *args, **kwargs):
        self.full_clean(exclude=['description'])
        super().save(*args, **kwargs)

    def clean(self):
        if self.object_hash != self._compute_hash(self.estimator):
            raise ValidationError(
                "object_hash '%s' should be set by the estimator '%s'" % (self.object_hash, self.estimator))
        # if already persisted, do not update estimator
        obj = self.get_by_hash(self.object_hash)
        if self.id and self.object_hash != getattr(obj, 'object_hash', None):
            raise ValidationError(
                "Cannot persist updated estimator '%s'.  Create a new Estimator object." % self.estimator)
