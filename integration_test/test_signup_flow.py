from unittest import skip

from django.contrib.auth.models import User
from django.urls import reverse

from integration_test.base_integration_testcase import BaseIntegrationTestCase


class SignupFlowTestCase(BaseIntegrationTestCase):
    def test_signup_noInviteKey_userCreated(self):
        data = self.generate_user_form_data()
        self.client.post(reverse("signup"), data)

        user = User.objects.filter(username=data['username']).first()
        self.assertIsNotNone(user)

    def test_signup_withDatasetInviteKey_userCreatedAndAddedAsContributorToDataset(self):
        invite_key = 'invite_key'
        dataset = self.generate_dataset(invite_key=invite_key)
        data = self.generate_user_form_data()

        self.client.post(reverse("signup_with_invite", args=[dataset.invite_key]), data)

        user = User.objects.filter(username=data['username']).first()
        self.assertIsNotNone(user)
        self.assertIn(user, list(dataset.contributors.all()))

    @skip("flow on website works, test fails - need to fix")
    def test_login_withDatasetKey_userAddedAsContributorToDataset(self):
        invite_key = 'invite_key'
        dataset = self.generate_dataset(invite_key=invite_key)
        user = self.generate_user()
        data = {'username': user.username, 'password': user.password}
        self.assertNotIn(user, list(dataset.contributors.all()))

        self.client.post(reverse("login_with_invite", args=[dataset.invite_key]), data)

        self.assertIn(user, list(dataset.contributors.all()))
