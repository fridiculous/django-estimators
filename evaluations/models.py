import os

import dill
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models

# original based on sci-kit hashing function
from estimators import ESTIMATOR_UPLOAD_DIR, hashing
from estimators.managers import EstimatorManager


class EvaluationJob(models.Model):

    create_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    estimator_id = models.ForeignKey('estimators.Estimator', on_delete=models.CASCADE, null=False, blank=False)
    feature_matrix_id = models.ForeignKey('datasets.FeatureMatrix', on_delete=models.CASCADE, null=False, blank=False)
    target_vector_id = models.ForeignKey('datasets.TargetVector', on_delete=models.CASCADE, blank=True)

    class Meta:
        db_table = 'evaluation_jobs'

    def __repr__(self):
        return '<EvaluationJob <Id %s> <FeatureMatrix Id %s + Estimator Id %s>' % (self.id, self.feature_matrix_id, self.estimator_id)
