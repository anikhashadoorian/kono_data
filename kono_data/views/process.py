from urllib.parse import quote

from django.contrib import messages
from django.shortcuts import redirect, render

from data_model.enums import TaskType
from data_model.models import Dataset, Label
from data_model.utils import get_unprocessed_task
from kono_data.process_forms import task_type_to_process_form
from kono_data.utils import get_s3_bucket_from_str


class UnknownTaskTypeException(Exception):
    pass


def process(request, **kwargs):
    context = {}

    user = request.user
    dataset_id = kwargs.get('dataset')
    dataset = Dataset.objects.filter(id=dataset_id).first()

    if not dataset.is_user_authorised_to_contribute(user):
        messages.error(request, 'You\'re not authorized to process this dataset =(')
        return redirect('index')

    form_class = task_type_to_process_form[dataset.task_type]
    form = form_class(request.POST or None, labels=dataset.possible_labels)

    if form.is_valid():
        if user.is_anonymous:
            messages.info(request, 'Sign up or Login to label this dataset')
        else:
            task = form.data.get('task')
            Label.objects.create(user=user, dataset=dataset, task=task, data=form.cleaned_data)
        return redirect("process", dataset=dataset_id)

    context['form'] = form
    context['dataset'] = dataset
    if not dataset.tasks:
        if dataset.is_user_authorised_admin(user):
            messages.info(request, f'Dataset "{dataset}" has no tasks. Fetch new data to start processing')
            return redirect("update_or_create_dataset", dataset=dataset_id)
        else:
            messages.info(request,
                          f'Dataset "{dataset}" has no tasks. Ask your admin to fetch data to start processing')
            return redirect("index")

    task = get_unprocessed_task(user, dataset)
    bucket = get_s3_bucket_from_str(dataset.source_uri)
    if task:
        # TODO: change to function which adds to context dict depending on TaskType
        if dataset.task_type == TaskType.single_image_label.value:
            encoded_task = quote(task)
            context['task'] = task
            context['task_source'] = f'https://s3-{dataset.source_region}.amazonaws.com/{bucket}/{encoded_task}'
        elif dataset.task_type == TaskType.two_image_comparison.value:
            context['tasks'] = task
            context['task_sources'] = [f'https://s3-{dataset.source_region}.amazonaws.com/{bucket}/{quote(t)}'
                                       for t in task]
        else:
            raise UnknownTaskTypeException

    context['partial_name'] = 'partials/process_' + dataset.task_type + '.html'
    return render(request, "process.html", context)
