from datetime import datetime

import factory
import factory.fuzzy
import numpy as np
from factory.django import FileField as DjangoFileField
from factory.django import DjangoModelFactory
from sklearn.ensemble import RandomForestClassifier

from estimators import hashing
from estimators.models import DataSet, Estimator, EvaluationResult

__all__ = ['EstimatorFactory', 'DataSetFactory', 'EvaluationResultFactory']


def compute_hash(obj):
    return hashing.hash(obj)


def random_array(min_value=0, max_value=100, shape=(100, )):
    return np.random.randint(min_value, max_value, shape)


class EstimatorFactory(DjangoModelFactory):

    class Meta:
        model = Estimator
        django_get_or_create = ('object_hash',)

    estimator = factory.Iterator([
        RandomForestClassifier(),
    ])

    create_date = factory.LazyFunction(datetime.now)
    object_hash = factory.LazyAttribute(lambda o: compute_hash(o.estimator))
    object_file = DjangoFileField(
        filename=lambda o: 'files/estimators/%s' % o.object_hash)


class DataSetFactory(DjangoModelFactory):

    class Meta:
        model = DataSet
        django_get_or_create = ('object_hash',)

    class Params:
        min_random_value = 0
        max_random_value = 100
        shape = (100, )

    data = factory.LazyAttribute(lambda o: random_array(
        min_value=o.min_random_value,
        max_value=o.max_random_value,
        shape=o.shape,
    ))

    create_date = factory.LazyFunction(datetime.now)
    object_hash = factory.LazyAttribute(lambda o: compute_hash(o.data))
    object_file = DjangoFileField(
        filename=lambda o: 'files/datasets/%s' % o.object_hash)


class EvaluationResultFactory(DjangoModelFactory):

    class Meta:
        model = EvaluationResult

    create_date = factory.LazyFunction(datetime.now)
    _estimator_proxy = factory.SubFactory(EstimatorFactory)
    _X_test_proxy = factory.SubFactory(DataSetFactory, shape=(100, 3))
    _y_test_proxy = factory.SubFactory(DataSetFactory)
    _y_predicted_proxy = factory.SubFactory(DataSetFactory)
