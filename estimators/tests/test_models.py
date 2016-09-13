import os
import tempfile

from django.core.exceptions import ValidationError
from django.test import TestCase
from estimators.models import Estimator


class EstimatorCase(TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()

    def test_estimator_hash(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            m = Estimator(estimator=object, description='object test')
            m.save()
            self.assertEquals(m.estimator, object)
            del m

            n = Estimator.objects.get(description='object test')
            # sklearn hash of a object = 'd9c9f286391652b89978a6961b52b674'
            self.assertEqual(n.estimator_hash, 'd9c9f286391652b89978a6961b52b674')
            # assert loaded after calling n.estimator
            self.assertEquals(n.estimator, object)
            self.assertEquals(Estimator._compute_hash(object), 'd9c9f286391652b89978a6961b52b674')

    def test_estimator_persistance(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            m = Estimator(estimator=object, description='another object')
            self.assertEqual(os.path.exists(m.estimator_file.path), False)
            self.assertEqual(m.is_estimator_persisted, False)

            m.save()
            self.assertEqual(os.path.exists(m.estimator_file.path), True)
            self.assertEqual(m.is_estimator_persisted, True)

    def test_get_or_create(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            m = Estimator.get_or_create('new_original_object')
            m.save()
            self.assertEquals(m.estimator, 'new_original_object')

            n = Estimator.get_or_create('new_original_object')
            self.assertEquals(m, n)

    def test_create_from_file(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            obj = "{'key': 'value'}"
            m = Estimator(estimator=obj)
            m.save()
            estimator_hash = m.estimator_hash
            file_path = m.estimator_file.name
            del m

            m = Estimator.create_from_file(file_path)
            self.assertEquals(m.estimator, obj)
            self.assertEquals(m.estimator_hash, estimator_hash)

    def test_update_estimator_fail(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            m = Estimator(estimator='uneditable_object')
            m.estimator = 'object_edited_before_persistance'
            m.save()
            m.estimator = 'object_edited_after_persistance'
            self.assertRaises(ValidationError, m.save)

    def test_hashing_func(self):
        estimator_hash = Estimator._compute_hash('abcd')
        self.assertEqual(estimator_hash, '3062a9e3345c129799bd2c1603c2e966')

    def test_estimator_hash_diff_fail(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            m = Estimator()
            m.estimator_hash = 'randomly set hash'
            self.assertRaises(ValidationError, m.save)

            m = Estimator(estimator='unique_object')
            m.estimator_hash = 'randomly set hash'
            self.assertRaises(ValidationError, m.save)

    def tearDown(self):
        self.tmp_dir.cleanup()
