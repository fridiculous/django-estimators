import os

from pip.req import parse_requirements
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements(
    os.path.join(os.path.dirname(__file__), 'requirements.txt'), session=False)
reqs = [str(ir.req) for ir in install_reqs]

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-estimators',
    version='0.1.0.dev',
    packages=find_packages(),
    include_package_data=True,
    install_requires=reqs,
    license='MIT License',  # example license
    description='A django model to persist and track machine learning models',
    long_description=README,
    url='https://github.com/fridiculous/django-estimators',
    author='Simon Frid',
    author_email='simon.frid@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Version Control',
    ],
    keywords='scikit-learn, machine learning, ml, estimators, version control'
)
