from typing import Dict
from urllib.parse import quote

from data_model.enums import TaskType, UnknownTaskTypeException
from kono_data.utils import get_s3_bucket_from_str


def get_view_context_for_task(task) -> Dict:
    bucket = get_s3_bucket_from_str(task.dataset.source_uri)
    if task.dataset.task_type == TaskType.single_image_label.value:
        encoded_task = quote(task.definition)
        return {'task': task,
                'task_id': task.id,
                'task_source': f'https://s3-{task.dataset.source_region}.amazonaws.com/{bucket}/{encoded_task}'}
    elif task.dataset.task_type == TaskType.two_image_comparison.value:
        return {'task': task,
                'task_id': task.id,
                'task_sources': [f'https://s3-{task.dataset.source_region}.amazonaws.com/{bucket}/{quote(t)}'
                                 for t in task.definition.split(',')]}
    else:
        raise UnknownTaskTypeException()