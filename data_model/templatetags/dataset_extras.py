from django import template

from data_model.models import Dataset

register = template.Library()


@register.filter(name="get_invite_link_from_dataset_id")
def get_invite_link_from_dataset_id(dataset_id):
    return Dataset.objects.get(id=dataset_id).invite_link


@register.filter(name='split_slash')
def split_slash(value):
    return value.split('/')


@register.filter(name='dict_key')
def dict_key(dict, key):
    '''Returns the given key from a dictionary.'''
    return dict.get(key)
