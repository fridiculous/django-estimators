
import pytest
from django.core.exceptions import ValidationError

from estimators.models.estimators import Estimator
from estimators.tests.factories import EstimatorFactory


@pytest.mark.django_db
class TestEstimator():

    def test_estimator_persistance_without_factory(self):
        m = Estimator(estimator='new string', description='another object')
        assert m.object_file.storage.exists(m.object_file.path) == False
        assert m.is_persisted == False

        m.save()
        assert m.object_file.storage.exists(m.object_file.path) == True
        assert m.is_persisted == True

    def test_object_hash_with_factory(self):
        m = EstimatorFactory(estimator=object)
        assert m.estimator == object
        del m

        n = Estimator.objects.filter(estimator=object).first()
        # sklearn hash of a object = 'd9c9f286391652b89978a6961b52b674'
        assert n.object_hash == 'd9c9f286391652b89978a6961b52b674'
        # assert loaded after calling n.estimator
        assert n.estimator == object
        assert Estimator._compute_hash(
            object) == 'd9c9f286391652b89978a6961b52b674'

    def test_get_or_create(self):
        m, created = Estimator.objects.get_or_create(estimator='new_string_as_object')
        m.save()
        assert m.estimator == 'new_string_as_object'
        assert created == True

        n, created = Estimator.objects.get_or_create(estimator='new_string_as_object')
        assert m == n
        assert created == False

    def test_update_or_create(self):
        e = 'estimator_obj'
        m, created = Estimator.objects.update_or_create(estimator=e)
        m.save()
        assert m.estimator == e
        assert created == True

        n, created = Estimator.objects.update_or_create(estimator=e)
        assert m == n
        assert created == False

    def test_create_from_file_with_factory(self):
        obj = "{'key': 'value'}"
        m = EstimatorFactory(estimator=obj)
        object_hash = m.object_hash
        file_path = m.object_file.name
        del m

        m = Estimator.create_from_file(file_path)
        assert m.estimator == obj
        assert m.object_hash == object_hash
        assert m.is_persisted == False

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

    def test_hash_without_estimator_fail(self):
        m = Estimator()
        m.object_hash = 'randomly set hash'
        with pytest.raises(ValidationError):
            m.save()

    def test_wrong_hash_fail(self):
        m = Estimator(estimator='unique_object')
        m.object_hash = 'randomly set hash'
        with pytest.raises(ValidationError):
            m.save()
