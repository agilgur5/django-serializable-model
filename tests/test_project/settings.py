"""
Django settings for test_project project.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# required for running any Django tests
SECRET_KEY = 'test_secret_key'

# needed to discover models in Django tests
INSTALLED_APPS = [
    'test_app.apps.TestAppConfig'
]

# will use an in-memory database during testing when using sqlite3 engine
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
