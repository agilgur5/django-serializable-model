# django-serializable-model

Django classes to make your models, managers, and querysets serializable, with built-in support for related objects in ~100 LoC (shorter than this README!)


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

`.serialize` takes in any number of joins as its `*args` and they can be of any depth, using the same `__` syntax as `prefetch_related`. This means if your `Post` object also had `Comment` objects, you could write:

`User.objects.prefetch_related('post_set__comment_set').serialize('post_set__comment_set')`

and get an array of `Comment` dictionaries within each `Post` dictionary.


### JSON and APIs

Since `.serialize` outputs a dictionary, one can turn it into JSON simply by using `json.dumps` on the dictionary.

If you're building an API, you can use `JSONResponse` on the dictionary as well.


## How it works

Implementing a `.serialize` method on Models, Managers, and QuerySets allows for easily customizable whitelists and blacklists (among other things) on a per Model basis.
This type of behavior was not possible a simple recursive version of `model_to_dict`, but is often necessary for various security measures and overrides.
In order to recurse over relations / joins, it accepts the same arguments as the familiar `prefetch_related`, which, in my use cases, often immediately precedes the `.serialize` calls.
`.serialize` also uses a custom `model_to_dict` function that behaves a bit differently than the built-in one in a variety of ways that are more expected when building an API (see the docstring).

I'd encourage you to read the source code, since it's shorter than this README :)


## Compatibility

This is a good question. It was used in an older Django 1.5 codebase with Python 2.7. With Django 2.0 out, there are likely some changes that need to be made.


## Backstory

This library was built while I was working on [Yorango](https://github.com/Yorango)'s ad-hoc API. Writing code to serialize various models was complex and quite tedious, resulting in messy spaghetti code for many of our API methods. The only solutions I could find online were the [Django Full Serializers](http://code.google.com/p/wadofstuff/wiki/DjangoFullSerializers) from [wadofstuff](https://github.com/mattimustang/wadofstuff) as well as some recursive `model_to_dict` snippets online -- none of which gave the option for customizable whitelists and blacklists on a per Model basis.

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
