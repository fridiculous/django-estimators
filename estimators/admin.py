from django.contrib import admin

from estimators.models import DataSet, Estimator, EvaluationResult

admin.site.register(Estimator)
admin.site.register(DataSet)
admin.site.register(EvaluationResult)
