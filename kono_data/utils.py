from itertools import combinations
from random import sample
from typing import Optional, List, Tuple

from data_model.enums import TaskType, UnknownTaskTypeException


def get_s3_bucket_from_str(arn: str) -> Optional[str]:
    '''bucket can be given with S3 ARN prefix or not'''
    if 'arn:aws:s3:::' in arn:
        split_arn = arn.split(':::')
        return split_arn[1] if len(split_arn) > 0 else None
    else:
        return arn


def generate_comparison_tasks_from_keys(keys, ratio=0.5) -> List[Tuple[str, str]]:
    """
    :param keys: list of keys to be compared to each other
    :param ratio: ratio of comparison tasks to be opened for each key to all others.
                1 equals every image with each other
    :return: list of tasks = list of tuples of two keys
    """
    all_possible_combinations = list(combinations(keys, 2))
    nr_tasks = int(len(all_possible_combinations) * ratio)
    tasks = sample(all_possible_combinations, nr_tasks)
    tasks_as_str = [f'{k1},{k2}' for k1, k2 in tasks]
    return tasks_as_str


def process_form_data_for_tasktype(task, task_type, data):
    """
    two image comparison: needs to transform submitted data in boolean to selected image key.
    example: {'more_exciting': True} -> {'more_exciting': 'key_of_image_shown_to_the_right.png'}
    selection using toggle: False is left image, True is right image
    """
    if task_type == TaskType.single_image_label.value:
        return data
    elif task_type == TaskType.two_image_comparison.value:
        tasks = task.split(',')
        comparison_data = {}
        for k, v in data.items():
            if k != 'confirm':
                comparison_data[k] = tasks[1] if v else tasks[0]
        return comparison_data
    else:
        UnknownTaskTypeException()
