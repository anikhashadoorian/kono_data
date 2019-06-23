from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from data_model.enums import TaskType, UnknownTaskTypeException, LabelActionType
from data_model.models import Dataset, Label, Task
from data_model.utils import get_unprocessed_task, str_to_int
from kono_data.process_forms import task_type_to_process_form
from kono_data.utils import get_s3_bucket_from_str, process_form_data_for_tasktype

import logging

logger = logging.getLogger(__name__)


def process(request, **kwargs):
    context = {}

    user = request.user
    dataset_id = kwargs.get('dataset')
    dataset = Dataset.objects.filter(id=dataset_id).first()

    if not dataset.is_user_authorised_to_contribute(user):
        messages.error(request, 'You\'re not authorized to process this dataset =(')
        return redirect('index')

    form_class = task_type_to_process_form[dataset.task_type]
    form = form_class(request.POST or None, labels=dataset.label_names)

    if form.is_valid():
        if user.is_anonymous:
            messages.info(request, 'Sign up or Login to label this dataset')
        else:
            task_id = form.data.get('task_id')
            task = Task.objects.get(id=task_id)
            processing_time = form.data.get('processing-time')
            loading_time = form.data.get('loading-time')
            if processing_time:
                processing_time = str_to_int(processing_time)
            else:
                processing_time = -1

            if loading_time:
                loading_time = str_to_int(loading_time)
            else:
                loading_time = -1

            is_skip_action = LabelActionType.skip.value in request.POST
            if is_skip_action:
                data = {}
                action = LabelActionType.solve.skip.value
            else:
                data = process_form_data_for_tasktype(task, dataset.task_type, form.cleaned_data)
                action = LabelActionType.solve.value
            logger.info('Creating label with action {} for user {} in dataset {} - times: load {} processing {}'.format(
                action, user.id, dataset.id, loading_time, processing_time
            ))
            Label.objects.create(data=data, action=action, user=user, dataset=dataset, task=task,
                                 processing_time=processing_time, loading_time=loading_time)

        return redirect("process", dataset=dataset_id)

    context['form'] = form

    if not dataset.tasks.exists():
        if dataset.is_user_authorised_admin(user):
            messages.info(request, f'Dataset "{dataset}" has no tasks. Fetch new data to start processing')
            return redirect("update_or_create_dataset", dataset=dataset_id)
        else:
            messages.info(request,
                          f'Dataset "{dataset}" has no tasks. Ask your admin to fetch data to start processing')
            return redirect("index")

    context.update(get_task_context_for_view(dataset, user))
    return render(request, "process.html", context)


def get_task_context_for_view(dataset: Dataset, user: User):
    context = {'partial_name': 'partials/process_' + dataset.task_type + '.html',
               'dataset': dataset}
    task, is_first_task = get_unprocessed_task(user, dataset)
    if not task:
        return context

    context.update({'is_first_task': is_first_task,
                    'is_admin': dataset.is_user_authorised_admin(user)})
    bucket = get_s3_bucket_from_str(dataset.source_uri)
    if dataset.task_type == TaskType.single_image_label.value:
        encoded_task = quote(task.definition)
        context.update({'task': encoded_task,
                        'task_id': task.id,
                        'task_source': f'https://s3-{dataset.source_region}.amazonaws.com/{bucket}/{encoded_task}'})
    elif dataset.task_type == TaskType.two_image_comparison.value:
        context.update({'task': task.definition, 'task_id': task.id,
                        'task_sources': [f'https://s3-{dataset.source_region}.amazonaws.com/{bucket}/{quote(t)}'
                                         for t in task.definition.split(',')]})
    else:
        raise UnknownTaskTypeException()

    return context
