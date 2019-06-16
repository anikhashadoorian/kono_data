from django.test import Client
from django.urls import reverse

from integration_test.base_integration_testcase import BaseIntegrationTestCase


class ProcessingTestCase(BaseIntegrationTestCase):
    def setUp(self):
        self.client = Client()

    def test_processingTwoImageComparison_skip_skipLabelSaved(self):
        dataset = self.generate_dataset()
        self.generate_task(dataset=dataset)
        user = dataset.user

        data = {'username': user.username, 'password': user.password}
        response = self.client.post(reverse("login"), data)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("process", args=[str(dataset.id)]))
        self.assertEqual(response.status_code, 200)
