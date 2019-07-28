import base64
import itertools
from typing import Optional, Tuple

from django.contrib.auth.models import User
from django.db.models import F, QuerySet, Q, When, BooleanField, Case, Value, Func

from data_model.enums import TaskType
from data_model.models import Dataset, Task
from kono_data.utils import timing


@timing
def fetch_qs(qs):
    return qs.all()


@timing
def annotate_datasets_for_view(datasets: QuerySet, user: Optional[User] = None, n: int = None):
    datasets = datasets.only('id', 'title', 'description')
    annotated_fields = ['id', 'title', 'description', 'task_type']

    if user:
        if user.is_anonymous:
            annotated = datasets.annotate(
                is_user_authorised_to_contribute=F('is_public'))
            annotated_fields += ['is_user_authorised_to_contribute']
        else:
            annotated = datasets.annotate(
                is_user_authorised_admin=Case(
                    When(Q(user=user) | Q(admins__id=user.id), then=True),
                    default=False, output_field=BooleanField()))
            annotated = annotated.annotate(
                is_user_authorised_to_contribute=Case(
                    When(Q(is_public=False) & Q(is_user_authorised_admin=False) & ~Q(contributors__id=user.id),
                         then=False), default=True, output_field=BooleanField()))
            annotated_fields += ['is_user_authorised_admin', 'is_user_authorised_to_contribute']

    if n:
        annotated = annotated.order_by('-created_at')
        return annotated.values(*annotated_fields)[:n]

    return annotated.values(*annotated_fields)


@timing
def annotate_dataset_for_view(dataset: Dataset, user: User = None):
    dataset.nr_labels = dataset.labels.count()
    dataset.nr_tasks = dataset.tasks.count()

    if not user:
        return dataset

    if user.is_anonymous:
        dataset.is_user_authorised_to_contribute = dataset.is_public
    else:
        dataset.is_user_authorised_to_contribute = user in dataset.users
        dataset.is_user_authorised_admin = user == dataset.user or user in dataset.admins.all()
    return dataset


@timing
def get_unprocessed_tasks(user: User, dataset: Dataset, n: int) -> QuerySet:
    if dataset.task_type != TaskType.two_image_comparison.value:
        return dataset.tasks.filter(labels__isnull=True).order_by('?')[:n]

    annotated_qs = dataset.tasks.annotate(file1=Func(F('definition'), Value(','), Value(1), function='split_part'),
                                          file2=Func(F('definition'), Value(','), Value(2), function='split_part'))

    definitions_of_tasks_with_labels = annotated_qs.filter(labels__isnull=False).values_list('file1', 'file2')
    files_in_tasks_with_labels = list(itertools.chain.from_iterable(list(definitions_of_tasks_with_labels)))

    tasks_with_unlabeled_files = annotated_qs.exclude(file1__in=files_in_tasks_with_labels)

    if tasks_with_unlabeled_files.exists():
        return tasks_with_unlabeled_files.order_by('?')[:n]
    else:
        return dataset.tasks.filter(labels__isnull=True).order_by('?')[:n]


def get_unprocessed_task(user: User, dataset: Dataset) -> Tuple[Task, bool]:
    unprocessed_tasks = get_unprocessed_tasks(user, dataset, n=1)
    unprocessed_task = unprocessed_tasks[0] if unprocessed_tasks else None
    is_first_task = False if user.is_anonymous else not user.labels.filter(dataset=dataset).exists()
    return unprocessed_task, is_first_task


def get_dataset_from_invite_key(invite_key):
    if not invite_key:
        return None
    return Dataset.objects.filter(invite_key=invite_key).first()


def str_to_int(s):
    try:
        return int(s)
    except ValueError:
        return int(float(s))


def base64encode(s: str):
    return base64.b64encode(bytearray(s, 'utf-8')).decode()
