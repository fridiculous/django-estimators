from django.test import TestCase

from ml_model.services import MLModel
from ml_model.services import MLModelManager
import mock
import os
import tempfile

from django.core.exceptions import ValidationError


class MLModelManagerCase(TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()

    def test_unreferenced_files(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            n = MLModel(model=dict, description='keep object')
            n.save()
            del n

            m = MLModel(model=object, description='to be deleted object')
            m.save()
            filename = m.model_file.name
            m.delete()
            del m

            o = MLModel(model=list, description='file to be deleted')
            o.save()
            os.remove(os.path.join(self.tmp_dir.name, o.model_file.name))
            del o

            all_files = MLModelManager._get_unreferenced_files()
            self.assertEqual(all_files, {filename})

            num = MLModelManager.delete_unreferenced_files()
            self.assertEqual(num, 1)

            all_files = MLModelManager._get_unreferenced_files()
            self.assertEqual(len(all_files), 0)

    def test_empty_ml_models(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            n = MLModel(model=dict, description='keep object')
            n.save()
            del n

            m = MLModel(model=object, description='to be deleted object')
            m.save()
            m.delete()
            del m

            o = MLModel(model=list, description='file to be deleted')
            o.save()
            os.remove(os.path.join(self.tmp_dir.name, o.model_file.name))

            all_models = MLModelManager._get_empty_ml_models()
            self.assertEqual(all_models[0].model_hash, o.model_hash)

            deletion = MLModelManager.delete_empty_records()
            self.assertEqual(deletion[0], 1)

            all_models = MLModelManager._get_empty_ml_models()
            self.assertEqual(len(all_models), 0)

    def tearDown(self):
        self.tmp_dir.cleanup()
