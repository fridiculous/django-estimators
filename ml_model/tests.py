from django.test import TestCase

from ml_model.models import MLModel
import mock
import os
import tempfile

from django.core.exceptions import ValidationError


class MLModelCase(TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()

    def test_model_hash(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            m = MLModel(model=object, description='object test')
            m.save()
            self.assertEquals(m.model, object)
            del m

            n = MLModel.objects.get(description='object test')
            # sklearn hash of a object = 'd9c9f286391652b89978a6961b52b674'
            self.assertEqual(n.model_hash, 'd9c9f286391652b89978a6961b52b674')
            # assert loaded after calling n.model
            self.assertEquals(n.model, object)
            self.assertEquals(MLModel._hash_of_model(object), 'd9c9f286391652b89978a6961b52b674')

    def test_model_persistance(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            m = MLModel(model=object, description='another object')
            self.assertEqual(os.path.exists(m.model_file.path), False)
            self.assertEqual(m.is_model_persisted, False)

            m.save()
            self.assertEqual(os.path.exists(m.model_file.path), True)
            self.assertEqual(m.is_model_persisted, True)

    def test_get_or_create(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            m = MLModel.get_or_create('new_original_object')
            m.save()
            self.assertEquals(m.model, 'new_original_object')

            n = MLModel.get_or_create('new_original_object')
            self.assertEquals(m, n)

    def test_create_from_file(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            obj = "{'key': 'value'}"
            m = MLModel(model=obj)
            m.save()
            model_hash = m.model_hash
            file_path = m.model_file.name
            del m

            m = MLModel.create_from_file(file_path)
            self.assertEquals(m.model, obj)
            self.assertEquals(m.model_hash, model_hash)

    def test_update_model_fail(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            m = MLModel(model='uneditable_object')
            m.model = 'object_edited_before_persistance'
            m.save()
            m.model = 'object_edited_after_persistance'
            self.assertRaises(ValidationError, m.save)

    def test_hashing_func(self):
        model_hash = MLModel._hash_of_model('abcd')
        self.assertEqual(model_hash, '3062a9e3345c129799bd2c1603c2e966')

    def test_model_hash_diff_fail(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            m = MLModel()
            m.model_hash = 'randomly set hash'
            self.assertRaises(ValidationError, m.save)

            m = MLModel(model='unique_object')
            m.model_hash = 'randomly set hash'
            self.assertRaises(ValidationError, m.save)

    def tearDown(self):
        self.tmp_dir.cleanup()
