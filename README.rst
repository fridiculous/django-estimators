
.. image:: https://travis-ci.org/fridiculous/django-estimators.svg?branch=master
    :target: https://travis-ci.org/fridiculous/django-estimators

.. image:: https://landscape.io/github/fridiculous/django-estimators/master/landscape.svg?style=flat
   :target: https://landscape.io/github/fridiculous/django-estimators/master
   
Django-Estimators
==========

Machine Learning Versioning made Simple


Intro
-----
Django-Estimators helps persist and track machine learning models aka estimators.

You can use this to version models, track and deploy models.  It's highly extensible and can be used with almost any python object (scikit-learn, numpy arrays, modules, methods).

This repo utilizes django as an ORM.  If you'd like to work outside of django, try the sqlalchemy version `estimators <https://github.com/fridiculous/estimators.git>`_ instead.


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

3. Run `python manage.py shell` and get create new models like so
::
    from estimators.models import Estimator
    est = Estimator()

    # uses sklearn, but any object would work
    from sklearn.ensemble import RandomForestClassifier
    est.estimator = RandomForestClassifier()
    
    est.description = 'a simple stats model'
    est.save()

4.  Retrieve your model, using the usual django orm at a later time
::

    est = Estimator.objects.filter(description='a simple stats model')
    # now use your estimator
    est.estimator.predict(X)

Using with Notebook (or without django shell)
---------------------------------------------

In order to have access to the django db, you'll need to set up the environment variable to load up your django project.  In ipython, you can set the environment variable `DJANGO_SETTINGS_MODULE` to `your_project_name.settings` like so::

    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings")
    import django
    django.setup()

Now you can continue on as usual... ::

    from estimators.models import Estimator




Use Cases
---------

If you already have the model::

    est = Estimator.get_by_estimator(object)

If you know the unique hash of the model::

    est = Estimator.get_by_hash('358e500ba0643ec82d15cbfa8adc114c')


If you aren't sure if it exists, the recommended method is to use the `get_or_create` method::

    est = Estimator.get_or_create(object)

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
    from estimator.models import Evaluator

Now create your evaluation plan
::

    plan = Evaluator(X_test=X_test, y_test=y_test, estimator=rfc)

    result = plan.evaluate()

And you can view all the atributes on the plan

Development Installation 
------------------------

To install the latest version of django-estimators, clone the repo, change directory to the repo, and pip install it into your current virtual environment.::

    $ git clone git@github.com:fridiculous/django-estimators.git
    $ cd django-estimators
    $ <activate your project’s virtual environment>
    (virtualenv) $ pip install -e .  # the dot specifies for this current repo

