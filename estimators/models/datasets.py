
from django.db import models
from estimators.models.estimators import AbstractPersistObject


class DataSet(AbstractPersistObject):

    description = models.CharField(max_length=256)
    _data = None
    _object_property = '_data'

    _data = None

    class Meta:
        db_table = 'data_sets'

    @property
    def data(self):
        """return the dataframe, and load it into memory if it hasn't been loaded yet"""
        return self.get_object_as_property()

    @data.setter
    def data(self, obj):
        self.set_object_property(obj)

    def save(self, *args, **kwargs):
        self.full_clean(exclude=['description'])
        super().save(*args, **kwargs)

    def __repr__(self):
        return '<Dataset <Id %s - %s>>' % (self.id, str(self.data))
