import uuid

from django.contrib.auth.models import User
from django.test import TestCase

from data_model.enums import LabelActionType
from data_model.models import Dataset, Label


def add_to_dic_if_not_exist(dic: dict, key, value):
    if not dic.get(key):
        dic[key] = value


class BaseTestCase(TestCase):
    @classmethod
    def generate_dataset(cls, user=None, **kwargs):
        if not user:
            user = cls.generate_user()

        add_to_dic_if_not_exist(kwargs, 'title', 'TestDataset')
        add_to_dic_if_not_exist(kwargs, 'description', 'description')
        add_to_dic_if_not_exist(kwargs, 'is_public', True)
        add_to_dic_if_not_exist(kwargs, 'possible_labels', ['hotdog', 'not_hotdog'])
        return Dataset.objects.create(user=user, **kwargs)

    @classmethod
    def generate_user(cls, is_super_user=False, username=None, **kwargs):
        if not username:
            username = str(uuid.uuid4())

        add_to_dic_if_not_exist(kwargs, 'username', username)
        add_to_dic_if_not_exist(kwargs, 'email', '{}@kono_data.com'.format(username))
        add_to_dic_if_not_exist(kwargs, 'password', 'bestpassword123')

        bio = kwargs.pop('bio', 'Long long time ago..')
        location = kwargs.pop('location', 'Planet Earth')

        if is_super_user:
            user = User.objects.create_superuser(**kwargs)
        else:
            user = User.objects.create_user(**kwargs)

        user.profile.bio = bio
        user.profile.location = location
        user.save()
        return user

    @classmethod
    def generate_label(cls, user, dataset, **kwargs):
        add_to_dic_if_not_exist(kwargs, 'data', {})
        add_to_dic_if_not_exist(kwargs, 'action', LabelActionType.solve)
        add_to_dic_if_not_exist(kwargs, 'task', 'task')
        return Label.objects.create(user=user, dataset=dataset, **kwargs)
