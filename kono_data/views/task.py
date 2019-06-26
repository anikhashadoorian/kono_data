from django.shortcuts import redirect, render

from data_model.models import Task
from kono_data.utils import timing
from kono_data.views.views_utils import get_view_context_for_task


@timing
def show_task(request, **kwargs):
    task_id = kwargs.get('task')

    task = Task.objects.filter(id=task_id).first()
    labels = task.labels.all()

    context = {'task': task, 'labels': labels}
    context.update(get_view_context_for_task(task))
    return render(request, "show_task.html", context)
