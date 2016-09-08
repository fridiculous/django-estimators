import datetime
import os
import dill

from sklearn.externals import joblib

from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError

from django.db import models
from django.apps import apps
from django.conf import settings


class MLModel(models.Model):

    create_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    description = models.CharField(max_length=256)
    model_hash = models.CharField(max_length=64, unique=True, default=None, null=False, editable=False)
    model_file = models.FileField(upload_to=settings.MODELS_UPLOAD_DIR, default=None, null=False, blank=True, editable=False)
    _model = None

    class Meta:
        db_table = 'ml_model'

    def __repr__(self):
        return '<MLModel <Id %s> <Hash %s>: %s>' % (self.id, self.model_hash, self.model)

    @property
    def is_model_persisted(self):
        return self.model_file.name is not None and os.path.isfile(self.model_file.path)

    @classmethod
    def _hash_of_model(cls, model):
        return joblib.hash(model)

    @classmethod
    def get_by_model(cls, model):
        if model is not None:
            model_hash = cls._hash_of_model(model)
        return cls.get_by_model_hash(model_hash)

    @classmethod
    def get_by_model_hash(cls, model_hash):
        query_set = cls.objects.filter(model_hash=model_hash)
        return query_set.first()

    @classmethod
    def get_or_create(cls, model):
        model_hash = cls._hash_of_model(model)
        obj = cls.get_by_model_hash(model_hash)
        if not obj:
            # create object
            obj = cls()
            obj.model = model
        return obj

    @property
    def model(self):
        # return cached model into cache if the model is available in a file
        if self._model is None:
            self._load_model()
        return self._model

    @model.setter
    def model(self, model):
        model_hash = self._hash_of_model(model)
        self._model = model
        self.model_hash = model_hash
        self.model_file.name = self.model_hash

    def save(self, *args, **kwargs):
        self.full_clean(exclude=['description'])
        if not self.is_model_persisted:
            self._persist_model()
        super(MLModel, self).save(*args, **kwargs)

    def clean(self):
        if self.model_hash != self._hash_of_model(self.model):
            raise ValidationError("model_hash '%s' should be set by the model '%s'" % (self.model_hash, self.model))
        # if already persisted, do not update model
        obj = self.get_by_model_hash(self.model_hash)
        if self.id and self.model_hash != getattr(obj, 'model_hash', None):
            raise ValidationError("Cannot persist updated model '%s'.  Create a new MLModel object." % self.model)

    def _persist_model(self):
        if self.model_hash:
            data = dill.dumps(self.model)
            f = ContentFile(data)
            self.model_file.save(self.model_hash, f)
            f.close()
            return True
        return False

    def _load_model(self):
        # to force loading a model
        if self.is_model_persisted:
            self.model_file.open()
            self._model = dill.loads(self.model_file.read())
            self.model_hash = MLModel._hash_of_model(self._model)
            self.model_file.close()

    @classmethod
    def create_from_file(cls, filename):
        obj = cls()
        obj.model_file = filename
        obj._load_model()
        return obj
