import logging
import uuid
from typing import List
from itertools import combinations
from random import sample
import boto3
from botocore.exceptions import ClientError, ParamValidationError
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField, ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from markdownx.models import MarkdownxField

from data_model.enums import AwsRegionType, TaskType, LabelActionType
from data_model.model_utils import generate_invite_key
from kono_data.const import S3_ARN_PREFIX
from kono_data.utils import get_s3_bucket_from_str

logger = logging.getLogger(__name__)


class GenerateComparisonTasksException(Exception):
    pass


class Dataset(models.Model):
    class Meta:
        db_table = 'Dataset'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_datasets')
    source_uri = models.CharField(blank=False, null=False, max_length=128)
    source_region = models.CharField(choices=AwsRegionType.choices(),
                                     default=AwsRegionType.eu_west_1,
                                     max_length=128,
                                     help_text='Give the AWS region of the S3 bucket. Required to show the content')
    is_public = models.BooleanField(default=False)
    title = models.CharField(max_length=140, blank=False, null=False, help_text='Give your dataset a descriptive title')
    description = MarkdownxField(help_text='Additional information about your dataset')
    task_type = models.CharField(choices=TaskType.choices(),
                                 default=TaskType.single_image_label,
                                 max_length=128,
                                 help_text='Task Type: label a single image or compare two images')
    labels_per_task = models.PositiveSmallIntegerField(default=1,
                                                       help_text='How many labels should be saved for each task')
    label_names = ArrayField(models.CharField(max_length=128, blank=False),
                             help_text='Give a comma-separated list of the labels in your dataset. Example: "hotdog, not hotdog"')
    keys = ArrayField(models.CharField(max_length=256), null=True, blank=True)
    source_data = JSONField(default=dict,
                            help_text='Keys in your dataset, will be automatically fetched and overwritten each time you save.')
    admins = models.ManyToManyField(User, related_name='admin_datasets', blank=True)
    contributors = models.ManyToManyField(User, related_name='contributor_datasets', blank=True)
    invite_key = models.CharField(max_length=128, null=True)

    def __str__(self):
        return f'{self.title} - {self.source_region}'

    def clean_fields(self, exclude=None):
        if S3_ARN_PREFIX in self.source_uri:
            self.source_uri = self.source_uri.replace(S3_ARN_PREFIX, '')
        try:
            s3 = boto3.resource('s3')
            s3.meta.client.head_bucket(Bucket=self.source_uri)
        except ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = int(e.response['Error']['Code'])
            if error_code == 403:
                raise ValidationError('Private S3 bucket. Can\'t access data')
            elif error_code == 404:
                raise ValidationError('Could not find S3 bucket %s' % self.source_uri)
        except ParamValidationError as e:
            raise ValidationError('Wrong source bucket name. %s' % e)

    def save(self, *args, **kwargs):
        if not self.invite_key:
            self.invite_key = generate_invite_key(self)

        super(Dataset, self).save(*args, **kwargs)

    def fetch_keys_from_source(self):
        bucket_name = get_s3_bucket_from_str(str(self.source_uri))
        s3 = boto3.client('s3')
        paginator = s3.get_paginator('list_objects')
        page_response = paginator.paginate(Bucket=bucket_name)

        keys = []
        logger.info('start to fetch keys from bucket: %s', bucket_name)
        for response in page_response:
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                contents = response['Contents']
                keys += list(map(lambda obj: obj['Key'], contents))
                logger.info('received %s keys from bucket %s', len(contents), bucket_name)

        self.keys = keys
        if self.task_type == TaskType.two_image_comparison.value:
            prev_task_definitions = set(self.tasks.values_list('definition', flat=True))
            task_definitions = self.get_task_definitions_from_keys(keys=keys,
                                                                   prev_task_definitions=prev_task_definitions)

        else:
            task_definitions = keys

        Task.objects.bulk_create([
            Task(dataset=self, definition=definition) for definition in task_definitions
        ])
        self.save()

    @property
    def is_done(self) -> bool:
        return self.labels.count() >= self.nr_required_labels

    @property
    def nr_required_labels(self) -> int:
        return self.tasks.count() * self.labels_per_task

    def is_user_authorised_to_contribute(self, user: User) -> bool:
        if self.is_public:
            return True
        if user.is_anonymous:
            return False

        return self.user == user or user.admin_datasets.filter(id=self.id).exists() \
               or user.contributor_datasets.filter(id=self.id).exists()

    def is_user_authorised_admin(self, user: User) -> bool:
        if user.is_anonymous:
            return False
        else:
            return self.user == user or user.admin_datasets.filter(id=self.id).exists()

    @property
    def users(self):
        return User.objects.filter(Q(contributor_datasets=self) | Q(admin_datasets=self) | Q(owner_datasets=self))

    def get_leaderboard_users(self):
        return self.users.annotate(nr_labels=Count('labels',
                                                   filter=Q(labels__dataset=self,
                                                            labels__action=LabelActionType.solve.value))
                                   ).filter(nr_labels__gt=0).order_by('-nr_labels')

    @property
    def invite_link(self):
        return reverse('signup_with_invite', args=[str(self.invite_key)])

    def get_task_definitions_from_keys(self, keys: List[str],
                                       prev_task_definitions: List[str] = None,
                                       ratio: float = 0.1, max_nr_tasks: int = 100000) -> List[str]:
        """
        :param keys: list of keys to be compared to each other
        :param prev_tasks: list of previous tasks that should not be removed in new calculation
        :param ratio: ratio of comparison tasks to be opened for each key to all others.
                    1 means every key with all other keys
        :param max_nr_tasks: max number of tasks that can be returned.
                    return can be smaller depending on nr. of keys and ratio
        :return: list of tasks = list of tuples of two keys
        """

        if not prev_task_definitions:
            prev_task_definitions = []

        nr_prev_tasks = len(prev_task_definitions)
        if nr_prev_tasks >= max_nr_tasks:
            raise GenerateComparisonTasksException(
                f'Cannot generate new comparison tasks. {nr_prev_tasks} previous tasks'
                f' is more than {max_nr_tasks} max_nr_tasks')

        if ratio > 1:
            raise GenerateComparisonTasksException(f'Ratio {ratio} is larger 1. Duplicate task creation not supported')

        all_combinations = list(combinations(keys, 2))
        should_ignore_ratio = len(all_combinations) * ratio < len(keys)
        if should_ignore_ratio:
            ratio = 1

        all_combinations = set(all_combinations) - set(prev_task_definitions)
        nr_new_tasks = min(len(all_combinations) * ratio, max_nr_tasks - nr_prev_tasks)
        new_tasks = sample(all_combinations, int(nr_new_tasks))
        tasks_as_str = [f'{k1},{k2}' for k1, k2 in new_tasks]
        return tasks_as_str


class Task(models.Model):
    class Meta:
        db_table = 'Task'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='tasks')
    definition = models.CharField(max_length=256, null=False, blank=False)


class Label(models.Model):
    class Meta:
        db_table = 'Label'

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='labels')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='labels')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='labels')
    data = JSONField()
    action = models.CharField(choices=LabelActionType.choices(), max_length=64)
    processing_time = models.IntegerField(null=False, blank=False)
    loading_time = models.IntegerField(null=False, blank=False)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=254, blank=False, null=False)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    Profile.objects.get_or_create(user=instance)
    instance.profile.save()
