

from datasets.models import DataSet
from django.db import models
from estimators.models import Estimator


class EvaluationMixin(object):

    """A list of common methods and attributes for evaluations"""

    def _get_proxy_object(self, obj, ProxyKlass, proxy_klass_attribute):
        """ Returns the proxy object for an input object

        If the object is already the proxy object, return it.
        Otherwise set the appropriate proxy object to the proxy object's attribute
        """
        proxy_object = obj
        if not isinstance(obj, ProxyKlass):
            proxy_object = ProxyKlass(**{proxy_klass_attribute: obj})
        return proxy_object

    @property
    def estimator(self):
        return self._estimator_proxy.estimator

    @estimator.setter
    def estimator(self, obj):
        self._estimator_proxy = self._get_proxy_object(
            obj, Estimator, 'estimator')

    @property
    def X_test(self):
        return self._X_test_proxy.data

    @X_test.setter
    def X_test(self, obj):
        self._X_test_proxy = self._get_proxy_object(obj, DataSet, 'data')

    @property
    def y_test(self):
        return self._y_test_proxy.data

    @y_test.setter
    def y_test(self, obj):
        self._y_test_proxy = self._get_proxy_object(obj, DataSet, 'data')

    @property
    def y_predicted(self):
        return self._y_predicted_proxy.data

    @y_predicted.setter
    def y_predicted(self, obj):
        self._y_predicted_proxy = self._get_proxy_object(obj, DataSet, 'data')


class Evaluator(EvaluationMixin):

    """Instantiates an evaluation plan.

    An evaluator object takes an estimator, X_test and y_test as params.
    Those can be DataSet objects or data in themselves.

    Once set, the evaluator aka evaluation plan runs .evaluate()
    """

    def __init__(self, **options):
        self.estimator = options.pop('estimator', None)
        self.X_test = options.pop('X_test', None)
        self.y_test = options.pop('y_test', None)
        self.y_predicted = options.pop('y_predicted', None)

    def evaluate(self, persist=True):
        result = self.estimator.predict(self.X_test)

        options = {
            'y_predicted': result,
            'X_test': self.X_test,
            'y_test': self.y_test,
            'estimator': self.estimator,
        }
        er = EvaluationResult(**options)
        self.persist_results(er)
        return er

    def persist_results(self, er):
        er._estimator_proxy = er._estimator_proxy.__class__.get_or_create(
            er._estimator_proxy.estimator)
        er._X_test_proxy = er._X_test_proxy.__class__.get_or_create(
            er._X_test_proxy.data)
        er._y_test_proxy = er._y_test_proxy.__class__.get_or_create(
            er._y_test_proxy.data)
        er._y_predicted_proxy = er._y_predicted_proxy.__class__.get_or_create(
            er._y_predicted_proxy.data)
        er.save()

    def __repr__(self):
        return '<Evaluator(X_test=%s estimator=%s)>' % (
            self.X_test, self.estimator)


class EvaluationResult(EvaluationMixin, models.Model):

    create_date = models.DateTimeField(
        auto_now_add=True, blank=False, null=False)
    _estimator_proxy = models.ForeignKey(
        Estimator, on_delete=models.CASCADE, null=False, blank=False)
    _X_test_proxy = models.ForeignKey(
        DataSet,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='X_test')
    _y_test_proxy = models.ForeignKey(
        DataSet,
        on_delete=models.CASCADE,
        null=False,
        blank=True,
        related_name='y_test')
    _y_predicted_proxy = models.ForeignKey(
        DataSet,
        on_delete=models.CASCADE,
        null=True,
        related_name='y_predicted')

    class Meta:
        db_table = 'evaluation_results'

    def __repr__(self):
        return '<EvaluationResult <Id %s>' % (
            self.id)
