import pytest
from .models import User, Settings, Post


@pytest.mark.django_db
def test_whitelist():
    new_user = User.objects.create(
        name='John Doe',
        email='john@doe.com',
    )

    assert new_user.serialize() == {'name': 'John Doe'}


@pytest.mark.django_db
def test_one_to_one():
    new_user = User.objects.create(
        name='John Doe',
        email='john@doe.com',
    )
    Settings.objects.create(user=new_user)

    new_user_refreshed = (User.objects.select_related('settings')
        .get(pk=new_user.pk))

    assert new_user_refreshed.serialize() == {'name': 'John Doe'}
    # recursively serialize Settings object by passing the join in
    assert new_user_refreshed.serialize('settings') == \
        {'name': 'John Doe', 'settings': {'email_notifications': False}}


@pytest.mark.django_db
def test_foreign_key():
    new_user = User.objects.create(
        name='John Doe',
        email='john@doe.com',
    )
    Post.objects.create(user=new_user, text='wat a nice post')
    Post.objects.create(user=new_user, text='another nice post')

    serialized_posts = [
        {'id': 1, 'text': 'wat a nice post', 'user_id': 1},
        {'id': 2, 'text': 'another nice post', 'user_id': 1}
    ]

    # called on QuerySet
    # adds an _id to the foreign key name, just like when using `.values()`
    assert Post.objects.all().serialize() == serialized_posts

    # called on Manager
    assert User.objects.get(pk=new_user.pk).post_set.serialize() == \
        serialized_posts

    # recursively serialize Post objects by passing the join in
    assert (User.objects.prefetch_related('post_set').get(pk=new_user.pk)
        .serialize('post_set')) == \
        {'name': 'John Doe', 'post_set': serialized_posts}
