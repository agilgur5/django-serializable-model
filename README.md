# django-serializable-model

[![PyPI version](https://img.shields.io/pypi/v/django-serializable-model.svg)](https://pypi.org/project/django-serializable-model/)
[![releases](https://img.shields.io/github/tag-pre/agilgur5/django-serializable-model.svg)](https://github.com/agilgur5/django-serializable-model/releases)
[![commits](https://img.shields.io/github/commits-since/agilgur5/django-serializable-model/latest.svg)](https://github.com/agilgur5/django-serializable-model/commits/master)

[![dm](https://img.shields.io/pypi/dm/django-serializable-model.svg)](https://pypi.org/project/django-serializable-model/)
[![dw](https://img.shields.io/pypi/dw/django-serializable-model.svg)](https://pypi.org/project/django-serializable-model/)

Django classes to make your models, managers, and querysets serializable, with built-in support for related objects in ~100 LoC (shorter than this README!)

## Table of Contents

I. [Installation](#installation) <br />
II. [Usage](#usage) <br />
III. [How it Works](#how-it-works) <br />
IV. [Related Libraries](#related-libraries) <br />
V. [Backstory](#backstory)

## Installation

```shell
pip install django-serializable-model
```

It is expected that you already have Django installed

### Compatibility

_This was originally used in an older Django 1.5 codebase with Python 2.7._

Should work with Django 1.4-1.9 with Python 2.7-3.x.

- Likely works with Django 1.10-2.x, though not 100% sure that [`._meta.fields` usage works the same way in these](https://docs.djangoproject.com/en/2.0/ref/models/meta/#migrating-old-meta-api).
- `2to3` shows that there is nothing to change, so should be compatible with Python 3.x
- Likely works with Django 0.95-1.3 as well
  - Pre 0.95, the Manager API didn't exist, so some functionality may be limited in those versions, or it may just error on import
- Have not confirmed if this works with earlier versions of Python.

Please submit a PR or file an issue if you have a compatibility problem or have confirmed compatibility on versions.

<br>

## Usage

Simplest use case, just implements the `.serialize()` function on a model:

```python
from django.db import models
from django-serializable-model import SerializableModel


class User(SerializableModel):
    email = models.CharField(max_length=765, blank=True)
    name = models.CharField(max_length=100)


new_user = User.objects.create(
    name='John Doe',
    email='john@doe.com',
)

print new_user.serialize()
# {'id': 1, 'email': 'john@doe.com', 'name': 'John Doe'}
```

<br>

With an override of the default `.serialize()` function to only include whitelisted fields in the serialized dictionary:

```python
from django.db import models
from django-serializable-model import SerializableModel


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


new_user = User.objects.create(
    name='John Doe',
    email='john@doe.com',
)

print new_user.serialize()
# {'name': 'John Doe'}
```

<br>

With a simple, one-to-one relation:

```python
from django.db import models
from django-serializable-model import SerializableModel


class User(SerializableModel):
    email = models.CharField(max_length=765, blank=True)
    name = models.CharField(max_length=100)


class Settings(SerializableModel):
    user = models.OneToOneField(User, primary_key=True)
    email_notifications = models.BooleanField(default=False)

    def serialize(self, *args):
        """Override serialize method to not serialize the user field"""
        return super(Settings, self).serialize(*args, exclude=['user'])


new_user = User.objects.create(
    name='John Doe',
    email='john@doe.com',
)
Settings.objects.create(user=new_user)

new_user_refreshed = User.objects.select_related('settings').get(pk=new_user.pk)

print new_user_refreshed.serialize()
# {'id': 1, 'email': 'john@doe.com', 'name': 'John Doe'}

# recursively serialize Settings object by passing the join in
print new_user_refreshed.serialize('settings')
# {'id': 1, 'email': 'john@doe.com', 'settings': {'email_notifications': False}, 'name': 'John Doe'}
```

<br>

With a foreign key relation:

```python
from django.db import models
from django-serializable-model import SerializableModel


class User(SerializableModel):
    email = models.CharField(max_length=765, blank=True)
    name = models.CharField(max_length=100)


class Post(SerializableModel):
    user = models.ForeignKey(User)
    text = models.TextField()


new_user = User.objects.create(
    name='John Doe',
    email='john@doe.com',
)
Post.objects.create(user=new_user, text='wat a nice post')
Post.objects.create(user=new_user, text='another nice post')

# called on QuerySet
print Post.objects.all().serialize()
# [{'id': 1, 'text': 'wat a nice post', 'user_id': 1}, {'id': 2, 'text': 'another nice post', 'user_id': 1}]
# adds an _id to the foreign key name, just like when using `.values()`

# called on Manager
user1 = User.objects.get(pk=new_user.pk)
print user1.post_set.serialize()
# [{'id': 1, 'text': 'wat a nice post', 'user_id': 1}, {'id': 2, 'text': 'another nice post', 'user_id': 1}]

# recursively serialize Post objects by passing the join in
print User.objects.prefetch_related('post_set').get(pk=new_user.pk).serialize('post_set')
"""
{
    'id': 1,
    'email': 'john@doe.com',
    'name': 'John Doe',
    'post_set': [{'id': 1, 'text': 'wat a nice post', 'user_id': 1}, {'id': 2, 'text': 'another nice post', 'user_id': 1}]
}
"""
```

<br>

`.serialize` takes in any number of joins as its `*args` and they can be of any depth, using the same `__` syntax as [`prefetch_related`](https://docs.djangoproject.com/en/2.0/ref/models/querysets/#prefetch-related). This means if your `Post` object also had `Comment` objects, you could write:

```python
User.objects.prefetch_related('post_set__comment_set').serialize('post_set__comment_set')
```

and get an array of `Comment` dictionaries within each `Post` dictionary. If your `Post` object also had `Like` objects:

```python
joins = ['post_set__comment_set', 'post_set__like_set']
User.objects.prefetch_related(*joins).serialize(*joins)
```

<br>

### JSON and APIs

Since `.serialize` outputs a dictionary, one can turn it into JSON simply by using `json.dumps` on the dictionary.

If you're building an API, you can use `JSONResponse` on the dictionary as well.

<br>

## How it works

Implementing a `.serialize` method on Models, Managers, and QuerySets allows for easily customizable whitelists and blacklists (among other things) on a per Model basis.
This type of behavior was not possible a simple recursive version of `model_to_dict`, but is often necessary for various security measures and overrides.
In order to recurse over relations / joins, it accepts the same arguments as the familiar `prefetch_related`, which, in my use cases, often immediately precedes the `.serialize` calls.
`.serialize` also uses a custom `model_to_dict` function that behaves a bit differently than the built-in one in a variety of ways that are more expected when building an API (see the docstring).

I'd encourage you to read the source code, since it's shorter than this README :)

## Related Libraries

- [django-api-decorators](https://github.com/agilgur5/django-api-decorators)
  - `Tiny decorator functions to make it easier to build an API using Django in ~100 LoC`

<br>

## Backstory

This library was built while I was working on [Yorango](https://github.com/Yorango)'s ad-hoc API. Writing code to serialize various models was complex and quite tedious, resulting in messy spaghetti code for many of our API methods. The only solutions I could find online were the [Django Full Serializers](http://code.google.com/p/wadofstuff/wiki/DjangoFullSerializers) from [wadofstuff](https://github.com/mattimustang/wadofstuff) as well as some recursive `model_to_dict` snippets online -- none of which gave the option for customizable whitelists and blacklists on a per Model basis.
Later on, I found that [Django REST Framework's ModelSerializers](http://www.django-rest-framework.org/api-guide/serializers#modelserializer) do offer similar functionality to what I was looking for (and _without_ requiring buy-in to the rest of the framework), albeit with some added complexity and robustness.

I ended up writing my own solution in ~100 LoC that handled basically all of my needs and replaced a ton of messy serialiazation code from all around the codebase. It was used in production with fantastic results, including on queries with quite the complexity and depth, such as:

```python

    joins = ['unit_set', 'unit_set__listing_set',
        'unit_set__listing_set__tenants', 'unit_set__listing_set__bill_set',
        'unit_set__listing_set__payment_set__payer',
        'unit_set__listing_set__contract']
    s_props = (user.property_set.all().prefetch_related(*joins)
        .serialize(*joins))

```

Had been meaning to extract and open source this as well as other various useful utility libraries I had made at Yorango and finally got the chance!
