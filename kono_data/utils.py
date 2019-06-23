import logging
import time
from typing import Optional
import requests

import boto3

from data_model.enums import TaskType, UnknownTaskTypeException

logger = logging.getLogger(__name__)


def get_s3_bucket_from_str(arn: str) -> Optional[str]:
    '''bucket can be given with S3 ARN prefix or not'''
    if 'arn:aws:s3:::' in arn:
        split_arn = arn.split(':::')
        return split_arn[1] if len(split_arn) > 0 else None
    else:
        return arn


def process_form_data_for_tasktype(task: 'Task', task_type, data):
    """
    two image comparison: needs to transform submitted data in boolean to selected image key.
    example: {'more_exciting': True} -> {'more_exciting': 'key_of_image_shown_to_the_right.png'}
    selection using toggle: False is left image, True is right image
    """
    if task_type == TaskType.single_image_label.value:
        return data
    elif task_type == TaskType.two_image_comparison.value:
        labels = task.definition.split(',')
        comparison_data = {}
        for k, v in data.items():
            if k != 'confirm':
                comparison_data[k] = labels[1] if v else labels[0]
        return comparison_data
    else:
        UnknownTaskTypeException()


def timing(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('{} took {:2.2f} ms'.format(method.__name__, (te - ts) * 1000))
        return result

    return timed


def delete_s3_object(bucket, path):
    s3 = boto3.client('s3')
    resp = s3.delete_object(Bucket=bucket, Key=path)
    status_code = resp['ResponseMetadata']['HTTPStatusCode']
    return status_code in [200, 204]