from django.test import Client

from integration_test.base_integration_testcase import BaseIntegrationTestCase


class ProcessingTestCase(BaseIntegrationTestCase):
    def setUp(self):
        self.client = Client()

    def test_processingTwoImageComparison_skip_skipLabelSaved(self):
        pass
