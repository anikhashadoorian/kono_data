from graphene.test import Client
from data_model.schema import schema
from integration_test.base_integration_testcase import BaseIntegrationTestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser
from collections import OrderedDict
from data_model.utils import base64encode


class GraphqlTestCase(BaseIntegrationTestCase):
    def setUp(self):
        self.client = Client(schema=schema)

    def test_getGraphiqlEndpoint_statusCode200(self):
        dataset = self.generate_dataset(is_public=True)
        base64_dataset_id = base64encode(f'DatasetNode:{dataset.id}')
        req = RequestFactory().get('/')
        req.user = AnonymousUser()

        response = self.client.execute('''
        {
          datasets {
            edges {
              node {
                id
              }
            }
          }
        }
        ''', context_value=req)

        self.assertEqual(response['data']['datasets']['edges'][0]['node']['id'], base64_dataset_id)
