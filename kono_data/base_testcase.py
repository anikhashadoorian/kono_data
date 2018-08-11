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
    def generate_user_form_data(cls) -> dict:
        return {**cls.generate_user_data(),
                **{'password1': 'bestpassword123',
                   'password2': 'bestpassword123'}
                }

    @classmethod
    def generate_user_data(cls) -> dict:
        username = '{}@konodata.com'.format(uuid.uuid4())
        return {'username': username,
                'email': username,
                'password': 'bestpassword123',
                'bio': 'Long long time ago..',
                'location': 'Planet Earth'}

    @classmethod
    def generate_user(cls, is_super_user=False, **kwargs) -> User:
        user_data = cls.generate_user_data()
        user_data.update(kwargs)
        bio = user_data.pop('bio')
        location = user_data.pop('location')

        if is_super_user:
            user = User.objects.create_superuser(**user_data)
        else:
            user = User.objects.create_user(**user_data)

        user.profile.bio = bio
        user.profile.location = location
        user.save()
        return user

    @classmethod
    def generate_label(cls, user, dataset, **kwargs):
        add_to_dic_if_not_exist(kwargs, 'data', {})
        add_to_dic_if_not_exist(kwargs, 'action', LabelActionType.solve)
        add_to_dic_if_not_exist(kwargs, 'task', 'task')
        add_to_dic_if_not_exist(kwargs, 'processing_time', 2342)
        return Label.objects.create(user=user, dataset=dataset, **kwargs)
