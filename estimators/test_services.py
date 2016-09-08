from django.test import TestCase

from estimators.models import Estimator
from estimators.services import EstimatorManager
import mock
import os
import tempfile

from django.core.exceptions import ValidationError


class EstimatorManagerCase(TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()

    def test_unreferenced_files(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            n = Estimator(estimator=dict, description='keep object')
            n.save()
            del n

            m = Estimator(estimator=object, description='to be deleted object')
            m.save()
            filename = m.estimator_file.name
            m.delete()
            del m

            o = Estimator(estimator=list, description='file to be deleted')
            o.save()
            os.remove(os.path.join(self.tmp_dir.name, o.estimator_file.name))
            del o

            all_files = EstimatorManager._get_unreferenced_files()
            self.assertEqual(all_files, {filename})

            num = EstimatorManager.delete_unreferenced_files()
            self.assertEqual(num, 1)

            all_files = EstimatorManager._get_unreferenced_files()
            self.assertEqual(len(all_files), 0)

    def test_empty_records(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            n = Estimator(estimator=dict, description='keep object')
            n.save()
            del n

            m = Estimator(estimator=object, description='to be deleted object')
            m.save()
            m.delete()
            del m

            o = Estimator(estimator=list, description='file to be deleted')
            o.save()
            os.remove(os.path.join(self.tmp_dir.name, o.estimator_file.name))

            all_estimators = EstimatorManager._get_empty_records()
            self.assertEqual(all_estimators[0].estimator_hash, o.estimator_hash)

            deletion = EstimatorManager.delete_empty_records()
            self.assertEqual(deletion[0], 1)

            all_estimators = EstimatorManager._get_empty_records()
            self.assertEqual(len(all_estimators), 0)

    def tearDown(self):
        self.tmp_dir.cleanup()
