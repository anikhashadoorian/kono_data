from kono_data.base_testcase import BaseTestCase


class ModelsTestCase(BaseTestCase):
    def test_datasetModel_users_includeOwner(self):
        dataset = self.generate_dataset()

        self.assertIn(dataset.user, dataset.users)

    def test_datasetModel_users_includeContributor(self):
        dataset = self.generate_dataset()
        admin_user = self.generate_user()
        dataset.contributors.add(admin_user)

        self.assertIn(dataset.user, dataset.users)

    def test_datasetModel_users_includeAdmin(self):
        dataset = self.generate_dataset()
        admin_user = self.generate_user()
        dataset.admins.add(admin_user)
        self.assertIn(dataset.user, dataset.users)
