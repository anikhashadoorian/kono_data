from django import template

from data_model.models import Dataset

register = template.Library()


@register.filter(name="get_invite_link_from_dataset_id")
def get_invite_link_from_dataset_id(dataset_id):
    return Dataset.objects.get(id=dataset_id).invite_link
