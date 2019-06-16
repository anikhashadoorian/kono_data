from django.test import Client

from kono_data.base_testcase import BaseTestCase


class IndexTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = cls.generate_user()

    def test_indexView_anonymousUser_validResponse(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_indexView_userLogin_validResponse(self):
        response = self.client.post('/accounts/login/', {'email': 'self.user.email',
                                                         'password': 'self.user.password'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
