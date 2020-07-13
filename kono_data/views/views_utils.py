from typing import Dict
from urllib.parse import quote

import boto3
from botocore.config import Config

from data_model.enums import TaskType, UnknownTaskTypeException
from data_model.models import Task
from kono_data.utils import get_s3_bucket_from_str

s3_session = boto3.session.Session(region_name='eu-west-1')
s3_client = s3_session.client('s3',
                              endpoint_url=f'https://s3.eu-west-1.amazonaws.com',
                              config=Config(signature_version='s3v4',
                                            s3={'addressing_style': 'virtual'}))


def get_signed_url(bucket, key, allow_stream=False):
    # allow_stream is for video files to stream instead of auto-downbload

    url_params = {
        'Bucket': bucket,
        'Key': key,
    }
    if allow_stream:
        url_params['ResponseContentType'] = 'application/octet-stream'

    return s3_client.generate_presigned_url('get_object', Params=url_params, HttpMethod="GET")


def get_view_context_for_task(task: Task) -> Dict:
    bucket = get_s3_bucket_from_str(task.dataset.source_uri)
    if task.dataset.task_type == TaskType.single_image_label.value:
        return {
            'task': task,
            'task_id': task.id,
            'task_source': get_signed_url(bucket, task.definition)
        }
    elif task.dataset.task_type == TaskType.two_image_comparison.value:
        return {
            'task': task,
            'task_id': task.id,
            'task_sources': [f'https://s3-{task.dataset.source_region}.amazonaws.com/{bucket}/{quote(t)}'
                             for t in task.definition.split(',')]
        }
    else:
        raise UnknownTaskTypeException()
