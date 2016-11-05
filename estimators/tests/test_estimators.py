import os
import tempfile

from django.core.exceptions import ValidationError
from django.test import TestCase
from estimators.models.estimators import Estimator


class EstimatorCase(TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()

    def test_object_hash(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            m = Estimator(estimator=object, description='object test')
            m.save()
            self.assertEquals(m.estimator, object)
            del m

            n = Estimator.objects.get(description='object test')
            # sklearn hash of a object = 'd9c9f286391652b89978a6961b52b674'
            self.assertEqual(n.object_hash, 'd9c9f286391652b89978a6961b52b674')
            # assert loaded after calling n.estimator
            self.assertEquals(n.estimator, object)
            self.assertEquals(Estimator._compute_hash(
                object), 'd9c9f286391652b89978a6961b52b674')

    def test_estimator_persistance(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            m = Estimator(estimator=object, description='another object')
            self.assertEqual(os.path.exists(m.object_file.path), False)
            self.assertEqual(m.is_persisted, False)

            m.save()
            self.assertEqual(os.path.exists(m.object_file.path), True)
            self.assertEqual(m.is_persisted, True)

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
            object_hash = m.object_hash
            file_path = m.object_file.name
            del m

            m = Estimator.create_from_file(file_path)
            self.assertEquals(m.estimator, obj)
            self.assertEquals(m.object_hash, object_hash)

    def test_update_estimator_fail(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            m = Estimator(estimator='uneditable_object')
            m.estimator = 'object_edited_before_persistance'
            m.save()
            m.estimator = 'object_edited_after_persistance'
            self.assertRaises(ValidationError, m.save)

    def test_hashing_func(self):
        object_hash = Estimator._compute_hash('abcd')
        self.assertEqual(object_hash, '3062a9e3345c129799bd2c1603c2e966')

    def test_object_hash_diff_fail(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            m = Estimator()
            m.object_hash = 'randomly set hash'
            self.assertRaises(ValidationError, m.save)

            m = Estimator(estimator='unique_object')
            m.object_hash = 'randomly set hash'
            self.assertRaises(ValidationError, m.save)

    def tearDown(self):
        self.tmp_dir.cleanup()
