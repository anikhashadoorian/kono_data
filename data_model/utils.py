from typing import Optional, Tuple

from django.contrib.auth.models import User
from django.db.models import F, QuerySet, Q, When, BooleanField, Case

from data_model.models import Dataset, Task
from kono_data.utils import timing

import base64

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


def get_unprocessed_tasks(user: User, dataset: Dataset, n: int) -> QuerySet:
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
