from django.test import TestCase

from estimators.models import Estimator
from estimators.managers import EstimatorManager
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

            all_files = Estimator.objects.unreferenced_files()
            self.assertEqual(all_files, {filename})

            num = Estimator.delete_unreferenced_files()
            self.assertEqual(num, 1)

            all_files = Estimator.objects.unreferenced_files()
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

            all_estimators = Estimator.objects.empty_records()
            self.assertEqual(all_estimators[0].estimator_hash, o.estimator_hash)

            deletion = Estimator.delete_empty_records()
            self.assertEqual(deletion[0], 1)

            all_estimators = Estimator.objects.empty_records()
            self.assertEqual(len(all_estimators), 0)

    def test_load_records(self):
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

            unreferenced_files = Estimator.objects.unreferenced_files()
            total_count = Estimator.objects.count()
            self.assertEqual(unreferenced_files, {filename})

            num = Estimator.load_unreferenced_files()
            self.assertEqual(num, 1)

            new_unreferenced_files = Estimator.objects.unreferenced_files()
            new_total_count = Estimator.objects.count()

            self.assertEqual(new_total_count, total_count+1)
            # Note this does not reflect the original file.  Instead it makes a duplicate file.
            self.assertEqual(len(unreferenced_files), len(new_unreferenced_files))

    def tearDown(self):
        self.tmp_dir.cleanup()
