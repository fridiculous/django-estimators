from django.db import models

from estimators.managers import (FeatureMatrixManager, PredictedManager,
                                 TargetManager)
from estimators.models import AbstractPersistObject


class FeatureMatrix(AbstractPersistObject):

    description = models.CharField(max_length=256)
    _dataframe = None
    _object_property = '_dataframe'

    class Meta:
        db_table = 'feature_datasets'

    def __repr__(self):
        return '<FeatureMatrix <Id %s> <Hash %s>' % (self.id, self.object_hash)

    objects = FeatureMatrixManager()

    @property
    def dataframe(self):
        """return the dataframe, and load it into memory if it hasn't been loaded yet"""
        return self.get_object_as_property()

    @dataframe.setter
    def dataframe(self, obj):
        self.set_object_property(obj)


class TargetVector(AbstractPersistObject):

    description = models.CharField(max_length=256)
    _array = None
    _object_property = '_array'

    class Meta:
        db_table = 'target_datasets'

    def __repr__(self):
        return '<TargetVector <Id %s> <Hash %s>' % (self.id, self.object_hash)

    objects = TargetManager()

    @property
    def array(self):
        """return the dataframe, and load it into memory if it hasn't been loaded yet"""
        return self.get_object_as_property()

    @array.setter
    def array(self, obj):
        self.set_object_property(obj)


class PredictedVector(AbstractPersistObject):

    description = models.CharField(max_length=256)
    _array = None
    _object_property = '_array'

    class Meta:
        db_table = 'predicted_datasets'

    def __repr__(self):
        return '<PredictedVector <Id %s> <Hash %s>' % (self.id, self.object_hash)

    objects = PredictedManager()

    @property
    def array(self):
        """return the dataframe, and load it into memory if it hasn't been loaded yet"""
        return self.get_object_as_property()

    @array.setter
    def array(self, obj):
        self.set_object_property(obj)
