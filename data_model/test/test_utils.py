from data_model.utils import get_unprocessed_task
from kono_data.base_testcase import BaseTestCase


class UtilsTestCase(BaseTestCase):
    def test_getUnprocessedTask_newUserAndDatasetGiven_unprocessedTaskAndIsFirstTaskTrueReturned(self):
        user = self.generate_user()
        dataset = self.generate_dataset()
        self.generate_task(dataset=dataset)

        unprocessed_task = get_unprocessed_task(user, dataset)

        self.assertIsNotNone(unprocessed_task)

    def test_getUnprocessedTask_activeUserAndDatasetGiven_unprocessedTaskAndIsFirstTaskFalseReturned(self):
        user = self.generate_user()
        dataset = self.generate_dataset()
        self.generate_task(dataset=dataset)
        self.generate_label(user, dataset)

        unprocessed_task = get_unprocessed_task(user, dataset)

        self.assertIsNotNone(unprocessed_task)


