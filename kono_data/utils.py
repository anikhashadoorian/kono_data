import logging
from itertools import combinations
from random import sample
from typing import Optional, List, Tuple

from data_model.enums import TaskType, UnknownTaskTypeException

logger = logging.getLogger(__name__)


def get_s3_bucket_from_str(arn: str) -> Optional[str]:
    '''bucket can be given with S3 ARN prefix or not'''
    if 'arn:aws:s3:::' in arn:
        split_arn = arn.split(':::')
        return split_arn[1] if len(split_arn) > 0 else None
    else:
        return arn


class GenerateComparisonTasksException(Exception):
    pass


def generate_comparison_tasks_from_keys(keys: List[str],
                                        prev_tasks: List[str] = None,
                                        ratio: float = 0.1,
                                        max_nr_tasks: int = 100000) -> List[str]:
    """
    :param keys: list of keys to be compared to each other
    :param prev_tasks: list of previous tasks that should not be removed in new calculation
    :param ratio: ratio of comparison tasks to be opened for each key to all others.
                1 means every key with all other keys
    :param max_nr_tasks: max number of tasks that can be returned.
                return can be smaller depending on nr. of keys and ratio
    :return: list of tasks = list of tuples of two keys
    """

    if not prev_tasks:
        prev_tasks = []

    if len(prev_tasks) >= max_nr_tasks:
        raise GenerateComparisonTasksException(f'Cannot generate new comparison tasks. {len(prev_tasks)} previous tasks'
                                               f' is more than {max_nr_tasks} max_nr_tasks')

    if ratio > 1:
        raise GenerateComparisonTasksException(f'Ratio {ratio} is larger 1. Duplicate task creation not supported')

    all_possible_combinations = list(combinations(keys, 2))
    should_ignore_ratio = len(all_possible_combinations) * ratio < len(keys)
    if should_ignore_ratio:
        ratio = 1

    nr_new_tasks = min(len(all_possible_combinations) * ratio, max_nr_tasks - len(prev_tasks))
    new_tasks = sample(all_possible_combinations, int(nr_new_tasks))
    tasks_as_str = [f'{k1},{k2}' for k1, k2 in new_tasks] + prev_tasks
    return list(set(tasks_as_str))


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
