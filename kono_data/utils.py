from itertools import combinations
from random import sample
from typing import Optional, List, Tuple


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
    return tasks
