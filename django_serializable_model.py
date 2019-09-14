import django
from django.db import models
from django.core.exceptions import ObjectDoesNotExist


# noqa | all models need an explicit or inferred app_label (https://stackoverflow.com/q/4382032/3431180)
# noqa | abstract models shouldn't though -- this is fixed in 1.8+ (https://code.djangoproject.com/ticket/24981)
# change __name__ instead of explicitly setting app_label as that would then
# need to be overridden by Models that extend this
if django.VERSION < (1, 8):
    __name__ = 'django_serializable_model.django_serializable_model'


class _SerializableQuerySet(models.query.QuerySet):
    """Implements the serialize method on a QuerySet"""
    def serialize(self, *args):
        serialized = []
        for elem in self:
            serialized.append(elem.serialize(*args))
        return serialized


class SerializableManager(models.Manager):
    """Implements table-level serialization via SerializableQuerySet"""
    # replaced by base_manager_name in Model.Meta in Django 1.10+
    if django.VERSION < (1, 10):
        # when queried from a related Model, use this Manager
        use_for_related_fields = True

    def get_queryset(self):
        return _SerializableQuerySet(self.model)

    # renamed to get_queryset in Django 1.6+
    if django.VERSION < (1, 6):
        get_query_set = get_queryset

    def get_queryset_compat(self):
        get_queryset = (self.get_query_set
                        if hasattr(self, 'get_query_set')
                        else self.get_queryset)
        return get_queryset()

    # implement serialize on the Manager itself (on .objects, before .all())
    def serialize(self, *args):
        return self.get_queryset_compat().serialize(*args)


class SerializableModel(models.Model):
    """
    Abstract Model that implements recursive serializability of models to
    dictionaries, both at the row and table level, with some overriding allowed
    """
    objects = SerializableManager()

    # this is needed due to the __name__ hackiness; will be incorrect and cause
    # Django to error when loading this model otherwise
    if django.VERSION < (1, 8):
        __module__ = 'django_serializable_model'

    class Meta:
        abstract = True

        # doesn't exist in <1.10, so Meta's typecheck will throw without guard
        if django.VERSION >= (1, 10):
            # when queried from a related Model, use this Manager
            base_manager_name = 'objects'

    def serialize(self, *args, **kwargs):
        """
        Serializes the Model object with model_to_dict_custom and kwargs, and
        proceeds to recursively serialize related objects as requested in args
        """
        serialized = model_to_dict_custom(self, **kwargs)
        args = list(args)  # convert tuple to list

        # iterate and recurse through all arguments
        index = 0
        length = len(args)
        while index < length:
            # split the current element
            field_with_joins = args[index]
            field, join = _split_joins(field_with_joins)
            all_joins = [join] if join else []  # empty string to empty array

            # delete it from the list
            del args[index]
            length -= 1

            # get all joins for this field from the arguments
            arg_joins = [_split_joins(arg, only_join=True)
                         for arg in args if arg.startswith(field)]
            all_joins += arg_joins  # combine all joins on this field

            # recurse if related object actually exists
            try:
                serialized[field] = getattr(self, field).serialize(*all_joins)
            except (AttributeError, ObjectDoesNotExist):
                pass

            # shrink length and remove all args that were recursed over
            length -= len(arg_joins)
            args = [arg for arg in args if not arg.startswith(field)]

        return serialized


def model_to_dict_custom(instance, fields=None, exclude=None, editable=True):
    """
    Custom model_to_dict function that differs by including all uneditable
    fields and excluding all M2M fields by default
    Also sets all ForeignKey fields to name + _id, similar to .values()
    """
    # avoid circular import
    from django.db.models.fields.related import ForeignKey
    opts = instance._meta
    data = {}
    for f in opts.fields:
        # skip uneditable fields if editable kwarg is False
        if not editable and not f.editable:
            continue
        # whitelisted fields only if fields kwarg is passed
        if fields and f.name not in fields:
            continue
        # blacklist fields from exclude kwarg
        if exclude and f.name in exclude:
            continue
        else:
            if isinstance(f, ForeignKey):
                data[f.name + '_id'] = f.value_from_object(instance)
            else:
                data[f.name] = f.value_from_object(instance)
    return data


def _split_joins(join_string, only_join=False):
    """
    Split a string into the field and it's joins, separated by __ as per
    Django convention
    """
    split = join_string.split('__')
    field = split.pop(0)  # the first field
    join = '__'.join(split)  # the rest of the fields

    # return single join or tuple based on kwarg
    if only_join:
        return join
    return field, join
