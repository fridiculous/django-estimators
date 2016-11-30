
.. image:: https://travis-ci.org/fridiculous/django-estimators.svg?branch=master
    :target: https://travis-ci.org/fridiculous/django-estimators

.. image:: https://coveralls.io/repos/github/fridiculous/django-estimators/badge.svg?branch=master
    :target: https://coveralls.io/github/fridiculous/django-estimators?branch=master

.. image:: https://landscape.io/github/fridiculous/django-estimators/master/landscape.svg?style=flat
   :target: https://landscape.io/github/fridiculous/django-estimators/master


Django-Estimators
=================

Tidy Persistance and Retrieval for Machine Learning


Intro
-----
Django-Estimators helps persist and track machine learning models (aka estimators) and datasets.


This library provides a series of proxy objects that wrap common python machine learning objects and dataset objects.  As a result, this library can be used to version, track progress and deploy models.  It's highly extensible and can be used with almost any python object (scikit-learn, numpy arrays, modules, methods).

This repo utilizes django as an ORM.  If you'd like to work outside of django, try the sqlalchemy-based `estimators <https://github.com/fridiculous/estimators.git>`_ library instead.


Installation
------------


Django-estimators is on PyPI, so just run: ::

    pip install django-estimators


Quick start
-----------

1. Add "estimators" to your INSTALLED_APPS django setting like this
::

    INSTALLED_APPS = [
        ...
        'estimators',
    ]
  
2. To create the estimators table, run
::
    python manage.py migrate

3. Run ``python manage.py shell`` and get create new models like so
::
    from sklearn.ensemble import RandomForestClassifier
    rfc = RandomForestClassifier()
    
    from estimators.models import Estimator
    est = Estimator(estimator=rfc)
    est.description = 'a simple forest'
    est.save()

4.  Retrieve your model, using the classic django orm, we can pull the last Estimator 
::

    est = Estimator.objects.last()
    # now use your estimator
    est.estimator.predict(X)


Use Case: Retrieving Models/Estimators
--------------------------------------

If you aren't sure if it exists, the recommended method is to use the `get_or_create` method
::

    est = Estimator.objects.get_or_create(estimator=object)
    # or potentially update it with update_or_create
    est = Estimator.objects.update_or_create(estimator=object)

If you already have the model, in this case of type object
::

    est = Estimator.objects.filter(estimator=object).first()

If you know the unique hash of the model
::

    est = Estimator.objects.filter(object_hash='d9c9f286391652b89978a6961b52b674').first()



Use Case: Persisting and Retrieving DataSets
--------------------------------------------

The `DataSet` class functions just like the `Estimator` class.  If you have
a numpy matrix or a pandas dataframe, you can wrap it with a DataSet object
::

    import numpy as np
    import pandas as pd

    df = pd.DataFrame(np.random.randint(0,10,(100,8)))

    from estimators.models import DataSet

    ds = DataSet(data=df)
    ds.save()

You can pull that same DataSet object later with
::

    ds = DataSet.objects.latest('create_date')

And if you already have the dataset
::

    ds = DataSet.objects.filter(data=df).first()


Use Case: Persisting Predictions and Results 
--------------------------------------------

Sometimes the most valuable part of a machine learning is the whole process.
Using an ``Evaluator`` object, we can define the relationships between X_test, y_test and
y_predicted ahead of time.

Then we can evaluate the evaluation plan, which in turn calls the ``predict`` method on the estimator
and then presists all the wrapped objects.

Here's a demo of using an Evaluator.
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

Now create your evaluation plan
::

    from estimators.models import Evaluator
    plan = Evaluator(X_test=X_test, y_test=y_test, estimator=rfc)

    result = plan.evaluate() # executes `predict` method on X_test

And you can view all the atributes on the evaluation result
::

    result.estimator
    result.X_test
    result.y_test # optional, used with supervised classifiers
    result.y_predicted


Using with Notebook (or without django shell)
---------------------------------------------

In order to have access to the django db, you'll need to set up the environment variable to load up your django project.  In ipython, you can set the environment variable ``DJANGO_SETTINGS_MODULE`` to ``your_project_name.settings`` like so::

    import os
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings")
    django.setup()

Now you can continue on as usual... ::

    from estimators.models import Estimator


Development Installation 
------------------------

To install the latest version of django-estimators, clone the repo, change directory to the repo, and pip install it into your current virtual environment.::

    $ git clone git@github.com:fridiculous/django-estimators.git
    $ cd django-estimators
    $ <activate your project’s virtual environment>
    (virtualenv) $ pip install -e .  # the dot specifies for this current repo
