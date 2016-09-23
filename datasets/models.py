from django.db import models

from estimators.managers import FeatureMatrixManager, TargetManager
from estimators.models import AbstractPersistObject


class FeatureMatrix(AbstractPersistObject):

    description = models.CharField(max_length=256)
    _dataframe = None
    _object_property = 'dataframe'

    class Meta:
        db_table = 'feature_datasets'

    def __repr__(self):
        return '<FeatureMatrix <Id %s> <Hash %s>' % (self.id, self.data_hash)

    objects = FeatureMatrixManager()


class TargetVector(AbstractPersistObject):

    description = models.CharField(max_length=256)
    _array = None
    _object_property = 'array'

    class Meta:
        db_table = 'target_datasets'

    def __repr__(self):
        return '<TargetVector <Id %s> <Hash %s>' % (self.id, self.target_hash)

    objects = TargetManager()
