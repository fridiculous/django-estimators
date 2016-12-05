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

    def filter(self, *args, **kwargs):
        """filter lets django managers use `objects.filter` on a hashable object."""
        obj = kwargs.pop(self.object_property_name, None)
        if obj is not None:
            kwargs['object_hash'] = self.model._compute_hash(obj)
        return super().filter(*args, **kwargs)

    def _extract_model_params(self, defaults, **kwargs):
        """this method allows django managers use `objects.get_or_create` and
        `objects.update_or_create` on a hashable object.
        """
        obj = kwargs.pop(self.object_property_name, None)
        if obj is not None:
            kwargs['object_hash'] = self.model._compute_hash(obj)
        lookup, params = super()._extract_model_params(defaults, **kwargs)
        if obj is not None:
            params[self.object_property_name] = obj
            del params['object_hash']
        return lookup, params


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
    def relative_path(self):
        return get_upload_path(self, self.object_file.name)

    @property
    def is_persisted(self):
        return self.object_file.name is not None and self.object_file.storage.exists(
            self.object_file.path)

    @classmethod
    def _compute_hash(cls, obj):
        return hashing.hash(obj)

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
        """Deprecated in favor for the canonical `objects.get_or_create` method"""
        raise DeprecationWarning('Please use `%s.objects.get_or_create()` instead' % cls)

    @classmethod
    def create_from_file(cls, filename):
        """Return an Estimator object given the path of the file, relative to the MEDIA_ROOT"""
        obj = cls()
        obj.object_file = filename
        obj.load()
        return obj
