from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from integration_test.base_integration_testcase import BaseIntegrationTestCase


class SignupTestCase(BaseIntegrationTestCase):
    def test_signup_withDatasetKey_userCreatedAsContributorToDataset(self):
        invite_key = 'invite_key'
        dataset = self.generate_dataset(invite_key=invite_key)
        data = self.generate_user_form_data()

        self.client.post(reverse("signup_with_invite", args=[dataset.invite_key]), data)

        user = User.objects.filter(username=data['username']).first()
        self.assertIsNotNone(user)
        self.assertIn(user, list(dataset.contributors.all()))
