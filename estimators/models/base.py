
import dill
from django.core.files.base import ContentFile
from django.db import models

from estimators import get_storage, get_upload_path, hashing


class PrimaryMixin(models.Model):

    create_date = models.DateTimeField(
        auto_now_add=True, blank=False, null=False)

    class Meta:
        abstract = True


class HashableFileQuerySet(models.QuerySet):

    object_property_name = NotImplementedError()

    def get_or_create(self, defaults=None, **kwargs):
        """
        Looks up an object with the given kwargs, creating one if necessary.
        Returns a tuple of (object, created), where created is a boolean
        specifying whether an object was created.
        """
        obj = kwargs.pop(self.object_property_name, None)
        if obj:
            kwargs['object_hash'] = self.model._compute_hash(obj)
        lookup, params = self._extract_model_params(defaults, **kwargs)
        if obj:
            params[self.object_property_name] = obj
            del lookup['object_hash']
        # The get() needs to be targeted at the write database in order
        # to avoid potential transaction consistency problems.
        self._for_write = True
        try:
            return self.get(**lookup), False
        except self.model.DoesNotExist:
            return self._create_object_from_params(lookup, params)


class HashableFileMixin(models.Model):

    create_date = models.DateTimeField(
        auto_now_add=True, blank=False, null=False)
    object_hash = models.CharField(
        max_length=64, unique=True, default=None, null=False, editable=False)
    object_file = models.FileField(
        upload_to=get_upload_path, storage=get_storage(), default=None, null=False, blank=True, editable=False)

    _object_property_name = NotImplementedError()

    objects = HashableFileQuerySet.as_manager()

    class Meta:
        abstract = True

    @property
    def is_persisted(self):
        return self.object_file.name is not None and self.object_file.storage.exists(
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
            self.object_file.save(self.object_hash, f, save=False)
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
