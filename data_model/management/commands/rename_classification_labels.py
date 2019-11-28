import json
import logging

from django.core.management.base import BaseCommand
from tqdm import tqdm

from data_model.models import Dataset

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('dataset_id', type=str)
        parser.add_argument('previous_to_current_name', type=str)  # {old_name1: new_name, old_name2: new_nameX}

    def handle(self, *args, **options):
        dataset_id = options['dataset_id']
        previous_to_current_name = json.loads(options['previous_to_current_name'])

        dataset = Dataset.objects.get(id=dataset_id)
        label_names = set(dataset.label_names)
        print(f'Currently live label names {label_names}')
        print(f'Previous to current name parameter {previous_to_current_name}')

        if not set(previous_to_current_name.values()).issubset(label_names):
            logger.info(
                f'Parameter previous to current name values {previous_to_current_name.values()} must be one of {label_names}')
            return

        for label in tqdm(list(dataset.labels.only('data').all())):
            saved_label_names = set(label.data.keys())
            if saved_label_names and not saved_label_names.issubset(label_names):
                diff_label_names = saved_label_names - label_names

                for diff_label_name in diff_label_names:
                    current_label_name = previous_to_current_name.get(diff_label_name)
                    if current_label_name:
                        logger.info(f'Copy value {label.data[
                            diff_label_name]} from key {diff_label_name} to key {current_label_name}')
                        label.data[current_label_name] = label.data[diff_label_name]
                        del label.data[diff_label_name]
                        label.save()
                    else:
                        logger.info(f'Could not find new label name for {diff_label_name}')
        logger.info(f'Done renaming classification labels')
