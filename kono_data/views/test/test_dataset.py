from django.test import Client
from django.urls import reverse

from kono_data.base_testcase import BaseTestCase


class DatasetTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = cls.generate_user()
        cls.dataset = cls.generate_dataset(user=cls.user)
        cls.generate_label(user=cls.user, dataset=cls.dataset)

    def test_showLeaderboardView_viewRequested_viewContainsLeaderboard(self):
        response = self.client.get(reverse('show_leaderboard', args=[self.dataset.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user.username, str(response.content))
