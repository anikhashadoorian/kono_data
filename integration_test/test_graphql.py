from django.test import Client

from integration_test.base_integration_testcase import BaseIntegrationTestCase


class GraphqlTestCase(BaseIntegrationTestCase):
    def setUp(self):
        self.client = Client()

    def test_getGraphiqlEndpoint_statusCode200(self):
        response = self.client.get('//graphiql#query=')

        self.assertEqual(response.status_code, 200)
