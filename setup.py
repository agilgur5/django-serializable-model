# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-serializable-model',
    version='0.0.3',
    description=('Django classes to make your models, managers, and ' +
                 'querysets serializable, with built-in support for related ' +
                 'objects in ~100 LoC'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/agilgur5/django-serializable-model',
    author='Anton Gilgur',
    license='Apache-2.0',
    classifiers=[
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',

        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'Framework :: Django :: 1.4',
        'Framework :: Django :: 1.5',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2'
    ],
    keywords=('django serializer serializers serializer-django serialize ' +
              'json dict queryset model modelmanager full wadofstuff'),
    py_modules=[
        'django_serializable_model',
        # this is the original, unintended name, and should be removed in the
        # first breaking/major release, v1.0.0. See `serializable.py` comment.
        'serializable'
    ],
    python_requires='>=2.7, <4',
    project_urls={  # Optional
        'Source': 'https://github.com/agilgur5/django-serializable-model/',
        'Tracker': 'https://github.com/agilgur5/django-serializable-model/issues', # noqa
    },
)
