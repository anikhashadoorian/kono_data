from django.test import Client
from django.urls import reverse

from kono_data.base_testcase import BaseTestCase


class DatasetTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = cls.generate_user()
        cls.dataset = cls.generate_dataset(user=cls.user)
        cls.task = cls.generate_task(dataset=cls.dataset)
        cls.generate_label(user=cls.user, task=cls.task, dataset=cls.dataset)

    def test_showTaskView_viewRequested_viewContainsLabel(self):
        response = self.client.get(reverse('task', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user.username, str(response.content))
