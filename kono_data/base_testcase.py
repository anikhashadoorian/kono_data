from django.contrib.auth.models import User
from django.test import TestCase


def add_to_dic_if_not_exist(dic: dict, key, value):
    if not dic.get(key):
        dic[key] = value


class BaseTestCase(TestCase):
    @classmethod
    def generate_dataset(cls):
        pass

    @classmethod
    def generate_user(cls, is_super_user=False, **kwargs):
        add_to_dic_if_not_exist(kwargs, 'username', 'username')
        add_to_dic_if_not_exist(kwargs, 'email', 'email@me.com')
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
    def generate_label(cls):
        pass
