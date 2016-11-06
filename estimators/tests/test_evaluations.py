import os
import tempfile

from django.test import TestCase


class EvaluationCase(TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()

    def test_evaluation_persistance(self):
        with self.settings(MEDIA_ROOT=self.tmp_dir.name):

            from sklearn.datasets import load_digits
            from sklearn.ensemble import RandomForestClassifier

            digits = load_digits()  # 1797 by 64
            X = digits.data
            y = digits.target

            # simple splitting for validation testing
            X_train, X_test = X[:1200], X[1200:]
            y_train, y_test = y[:1200], y[1200:]

            rfc = RandomForestClassifier()
            rfc.fit(X_train, y_train)

            from estimators.models import Evaluator

            ev = Evaluator(X_test=X_test, y_test=y_test, estimator=rfc)
            assert ev.X_test is X_test
            assert ev.y_test is y_test
            assert ev.estimator is rfc
            assert ev.y_predicted is None

            assert os.path.exists(
                ev._estimator_proxy.object_file.path) is False
            assert os.path.exists(ev._X_test_proxy.object_file.path) is False
            assert os.path.exists(ev._y_test_proxy.object_file.path) is False
            assert os.path.exists(
                ev._y_predicted_proxy.object_file.path) is False

            er = ev.evaluate()

            assert er.X_test is X_test
            assert er.y_test is y_test
            assert er.estimator is rfc
            assert er.y_predicted is not None
            assert len(er.y_predicted) == len(y_test)

            assert os.path.exists(er._estimator_proxy.object_file.path) is True
            assert os.path.exists(er._X_test_proxy.object_file.path) is True
            assert os.path.exists(er._y_test_proxy.object_file.path) is True
            assert os.path.exists(
                er._y_predicted_proxy.object_file.path) is True

    def tearDown(self):
        self.tmp_dir.cleanup()
