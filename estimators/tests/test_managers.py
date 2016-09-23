import os
import tempfile

from django.test import TestCase

from estimators.models import Estimator


class EstimatorManagerCase(TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()

    def test_unreferenced_files(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            kept = Estimator(estimator='object to be kept1')
            kept.save()
            no_obj = Estimator(estimator='object to be deleted1')
            no_obj.save()
            no_file = Estimator(estimator='file to be deleted1')
            no_file.save()

            filename = no_obj.object_file.name
            no_obj.delete()
            del no_obj

            os.remove(os.path.join(self.tmp_dir.name, no_file.object_file.name))
            del no_file

            # run tests
            all_files = Estimator.objects.unreferenced_files()
            self.assertEqual(all_files, {filename})

            num = Estimator.delete_unreferenced_files()
            self.assertEqual(num, 1)

            all_files = Estimator.objects.unreferenced_files()
            self.assertEqual(len(all_files), 0)

    def test_empty_records(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            kept = Estimator(estimator='object to be kept2')
            kept.save()
            no_obj = Estimator(estimator='object to be deleted2')
            no_obj.save()
            no_file = Estimator(estimator='file to be deleted2')
            no_file.save()

            no_obj.delete()
            del no_obj

            os.remove(os.path.join(self.tmp_dir.name, no_file.object_file.name))

            # run tests
            all_estimators = Estimator.objects.empty_records()
            self.assertEqual(all_estimators[0].object_hash, no_file.object_hash)

            deletion = Estimator.delete_empty_records()
            self.assertEqual(deletion[0], 1)

            all_estimators = Estimator.objects.empty_records()
            self.assertEqual(len(all_estimators), 0)

    def test_load_records(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):
            kept = Estimator(estimator='object to be kept3')
            kept.save()
            no_obj = Estimator(estimator='object to be deleted3')
            no_obj.save()
            no_file = Estimator(estimator='file to be deleted3')
            no_file.save()

            filename = no_obj.object_file.name
            no_obj.delete()
            del no_obj

            os.remove(os.path.join(self.tmp_dir.name, no_file.object_file.name))
            del no_file

            # run tests
            unreferenced_files = Estimator.objects.unreferenced_files()
            total_count = Estimator.objects.count()
            self.assertEqual(unreferenced_files, {filename})

            num = Estimator.load_unreferenced_files()
            self.assertEqual(num, 1)

            new_unreferenced_files = Estimator.objects.unreferenced_files()
            new_total_count = Estimator.objects.count()

            self.assertEqual(new_total_count, total_count + 1)
            # Note this does not reflect the original file.  Instead it makes a duplicate file.
            self.assertEqual(len(unreferenced_files), len(new_unreferenced_files))

    def tearDown(self):
        self.tmp_dir.cleanup()
