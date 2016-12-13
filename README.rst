
.. image:: https://travis-ci.org/fridiculous/django-estimators.svg?branch=master
    :target: https://travis-ci.org/fridiculous/django-estimators

.. image:: https://coveralls.io/repos/github/fridiculous/django-estimators/badge.svg?branch=master
    :target: https://coveralls.io/github/fridiculous/django-estimators?branch=master

.. image:: https://landscape.io/github/fridiculous/django-estimators/master/landscape.svg?style=flat
   :target: https://landscape.io/github/fridiculous/django-estimators/master


Django-Estimators
=================

Tidy Persistence and Retrieval for Machine Learning


Intro
-----
Django-Estimators helps persist and track machine learning models (aka estimators) and datasets.


This library provides a series of proxy objects that wrap common python machine learning objects and dataset objects.  This library versions, track progress and deploy models.  It's highly extensible and can be used with most any python object (scikit-learn, numpy arrays, modules, methods).

This repo utilizes django as an ORM.  If you'd like to work outside of django, try the sqlalchemy-based `estimators <https://github.com/fridiculous/estimators.git>`_ library instead.


Installation
------------


Run: 
::

    pip install django-estimators


Quick start
-----------

1. Add ``estimators`` to your INSTALLED_APPS.
::

    INSTALLED_APPS = [
        ...
        'estimators',
    ]
  
2. Create the estimators table.
::

    python manage.py migrate

3. Create a new model. Run ``python manage.py shell``
::

    from sklearn.ensemble import RandomForestClassifier
    rfc = RandomForestClassifier()
    
    from estimators.models import Estimator
    est = Estimator(estimator=rfc)
    est.description = 'a simple forest'
    est.save()

4.  Retrieve your model using the django orm.

    est = Estimator.objects.last()
    # now use your estimator
    est.estimator.predict(X)


Retrieving Models/Estimators
----------------------------

Use ``get_or_create`` to retrieve your model safely:
::

    est = Estimator.objects.get_or_create(estimator=object)
    # or potentially update it with update_or_create
    est = Estimator.objects.update_or_create(estimator=object)

If you have the model:

    est = Estimator.objects.filter(estimator=object).first()

Retrieve by unique hash:
::

    est = Estimator.objects.filter(object_hash='d9c9f286391652b89978a6961b52b674').first()



Persisting and Retrieving DataSets
----------------------------------

The `DataSet` class functions just like the `Estimator` class.  If you have
a numpy matrix or a pandas dataframe, wrap it with a DataSet object:
::

    import numpy as np
    import pandas as pd

    df = pd.DataFrame(np.random.randint(0,10,(100,8)))

    from estimators.models import DataSet

    ds = DataSet(data=df)
    ds.save()

Pull that same DataSet object with:
::

    ds = DataSet.objects.latest('create_date')

If you already have the dataset:
::

    ds = DataSet.objects.filter(data=df).first()


Persisting Predictions and Results 
----------------------------------

The most valuable part of a machine learning is the whole process.
Using an ``Evaluator`` object, define the relationships between X_test, y_test and
y_predicted ahead of time.

Then evaluate the evaluation plan, which in turn calls the ``predict`` method on the estimator
and then presists all the wrapped objects.

::

    from sklearn.datasets import load_digits
    from sklearn.ensemble import RandomForestClassifier
    
    digits = load_digits() # 1797 by 64
    X = digits.data
    y = digits.target
    
    # simple splitting for validation testing
    X_train, X_test = X[:1200], X[1200:]
    y_train, y_test = y[:1200], y[1200:]
    
    rfc = RandomForestClassifier()
    rfc.fit(X_train, y_train)

Create the evaluation plan:
::

    from estimators.models import Evaluator
    plan = Evaluator(X_test=X_test, y_test=y_test, estimator=rfc)

    result = plan.evaluate() # executes `predict` method on X_test

View all the atributes on the evaluation result:
::

    result.estimator
    result.X_test
    result.y_test # optional, used with supervised classifiers
    result.y_predicted


Using with Jupyter Notebook (or without a django app)
-----------------------------------------------------

Django-Estimators can run as a standalone django app. In order to have access to the django db, set up the environment variable to load up your django project.  In ipython, set the environment variable ``DJANGO_SETTINGS_MODULE`` to ``estimators.template_settings``:
::

    import os
    import django
    os.environ['DJANGO_SETTINGS_MODULE'] = "estimators.template_settings"
    django.setup()

When creating a new database (by default ``db.sqlite3``). Run this migration:
::

    from django.core.management import call_command
    call_command('migrate')


Continue as usual...
::

    from estimators.models import Estimator


To use custom settings, copy ``estimators.template_settings`` and edit the fields.  Like above, run ``os.environ['DJANGO_SETTINGS_MODULE'] = "custom_settings_file"`` before running ``django.setup()``.


Development Installation 
------------------------

To install the latest version of django-estimators, clone the repo, cd into the repo, and pip install with the current virtual environment.::

    $ git clone git@github.com:fridiculous/django-estimators.git
    $ cd django-estimators
    $ <activate your project’s virtual environment>
    (virtualenv) $ pip install -e .
