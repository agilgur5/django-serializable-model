"""
This is just a pure wrapper / alias module around django_serializable_model to
still be able to import it with the original, unintended name of serializable.
See https://github.com/agilgur5/django-serializable-model/issues/2

In the first major/breaking release, v1.0.0, this file should be deleted and
the module removed from `setup.py`.
"""

from django_serializable_model import *  # noqa F403, F401
