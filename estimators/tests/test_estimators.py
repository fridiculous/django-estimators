import os
import tempfile

from estimators.models.estimators import Estimator
from django.core.exceptions import ValidationError

import pytest


@pytest.mark.django_db
class TestEstimator():

    def test_object_hash(self):
        m = Estimator(estimator=object, description='object test')
        m.save()
        assert m.estimator == object
        del m

        n = Estimator.objects.get(description='object test')
        # sklearn hash of a object = 'd9c9f286391652b89978a6961b52b674'
        assert n.object_hash == 'd9c9f286391652b89978a6961b52b674'
        # assert loaded after calling n.estimator
        assert n.estimator == object
        assert Estimator._compute_hash(object) == 'd9c9f286391652b89978a6961b52b674'

    def test_estimator_persistance(self):
        m = Estimator(estimator=object, description='another object')
        assert os.path.exists(m.object_file.path) == False
        assert m.is_persisted == False

        m.save()
        assert os.path.exists(m.object_file.path) == True
        assert m.is_persisted == True

    def test_get_or_create(self):
        m = Estimator.get_or_create('new_original_object')
        m.save()
        assert m.estimator == 'new_original_object'

        n = Estimator.get_or_create('new_original_object')
        assert m == n

    def test_create_from_file(self):
        obj = "{'key': 'value'}"
        m = Estimator(estimator=obj)
        m.save()
        object_hash = m.object_hash
        file_path = m.object_file.name
        del m

        m = Estimator.create_from_file(file_path)
        assert m.estimator == obj
        assert m.object_hash == object_hash

    def test_update_estimator_fail(self):
        m = Estimator(estimator='uneditable_object')
        m.estimator = 'object_edited_before_persistance'
        m.save()
        m.estimator = 'object_edited_after_persistance'
        with pytest.raises(ValidationError):
            m.save()

    def test_hashing_func(self):
        object_hash = Estimator._compute_hash('abcd')
        assert object_hash == '3062a9e3345c129799bd2c1603c2e966'

    def test_object_hash_diff_fail(self):
        m = Estimator()
        m.object_hash = 'randomly set hash'
        with pytest.raises(ValidationError):
            m.save()

        m = Estimator(estimator='unique_object')
        m.object_hash = 'randomly set hash'
        with pytest.raises(ValidationError):
            m.save()
