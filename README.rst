=====
django-estimators
=====

django-estimators helps persist and track machine learning estimators aka models.

You can use this to version models, track and deploy models.  It's highly extensible and can be used with almost any python object (scikit-learn, numpy arrays, modules, methods).
-----




Quick start
-----------

1. Add "estimators" to your INSTALLED_APPS django setting like this::

    INSTALLED_APPS = [
        ...
        'estimators',
    ]

2. Run `python manage.py migrate` to create the estimators table.

3. Run `python manage.py shell` and get create new models like so::

	# uses sklearn, but any object would work
	from sklearn.ensemble import RandomForestClassifier
	rfc = RandomForestClassifer()

    from estimators.models import Estimator
    est = Estimator()
    est.estimator = rfc
    est.description = 'a simple stats model'
    est.save()



4.  Retrieve your model, using the usual django orm at a later time::

	from estimators.models import Estimator
	est = Estimator.objects.filter(description='a simple stats model')

	# now predict using a given feature matrix
	est.estimator.predict(X)


Using with Notebook (or without django shell)
---------------------------------------------

In order to have access to the django db, you'll need to set up the environment variable to load up your django project.  In ipython, you can set the environment variable `DJANGO_SETTINGS_MODULE` to `your_project_name.settings` like so::

	import os
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings")
    import django
    django.setup()

Now you can continue on as usual...::

	from estimators.models import Estimator


Use Cases
---------

If you already have the model::

	est = Estimator.get_by_estimator(object)

If you know the unique hash of the model::

	est = Estimator.get_by_estimator_hash('358e500ba0643ec82d15cbfa8adc114c')


If you aren't sure if it exists (Recommended Default Method)::

	est = Estimator.get_or_create(object)

