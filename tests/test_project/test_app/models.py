from django.db import models
from django_serializable_model import SerializableModel


class User(SerializableModel):
    email = models.CharField(max_length=765, blank=True)
    name = models.CharField(max_length=100)
    # whitelisted fields that are allowed to be seen
    WHITELISTED_FIELDS = set([
        'name',
    ])

    def serialize(self, *args, **kwargs):
        """Override serialize method to only serialize whitelisted fields"""
        fields = kwargs.pop('fields', self.WHITELISTED_FIELDS)
        return super(User, self).serialize(*args, fields=fields)


class Settings(SerializableModel):
    user = models.OneToOneField(User, primary_key=True,
        on_delete=models.CASCADE)
    email_notifications = models.BooleanField(default=False)

    def serialize(self, *args):
        """Override serialize method to not serialize the user field"""
        return super(Settings, self).serialize(*args, exclude=['user'])


class Post(SerializableModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
