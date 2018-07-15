import logging
import uuid

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
from django.utils import timezone

from data_model.enums import AwsRegionType, LabelingApproachEnum, TaskType, LabelActionType
from data_model.model_utils import generate_invite_key
from kono_data.const import S3_ARN_PREFIX
from kono_data.utils import get_s3_bucket_from_str, generate_comparison_tasks_from_keys

logger = logging.getLogger(__name__)


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
    description = models.TextField(max_length=1000, help_text='Additional information about your dataset')
    task_type = models.CharField(choices=TaskType.choices(),
                                 default=TaskType.single_image_label,
                                 max_length=128,
                                 help_text='Task Type: label a single image or compare two images')
    labeling_approach = models.CharField(choices=LabelingApproachEnum.choices(),
                                         default=LabelingApproachEnum.width_first,
                                         max_length=128,
                                         help_text='Choose a labeling approaching. This influences which keys are shown '
                                                   'to your users first. Only revelant if min_labels_per_key is larger than 1.'
                                                   'Width first: get a label for every key first and then reach the minimum labels per key.'
                                                   'Depth first: get the minimum labels per key first and then continue to other keys.')
    min_labels_per_key = models.PositiveSmallIntegerField(default=1,
                                                          help_text='How many labels should be saved for each key')
    possible_labels = ArrayField(
        models.CharField(max_length=128, blank=False),
        help_text='Give a comma-separated list of the labels in your dataset. Example: "hotdog, not hotdog"')
    keys = ArrayField(models.CharField(max_length=256), null=True, blank=True)
    tasks = ArrayField(models.CharField(max_length=256), blank=True, null=True)
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
                raise ValidationError('Private S3 bucket. Can\'t access keys to label')
            elif error_code == 404:
                raise ValidationError('Could not find S3 bucket %s' % self.source_uri)
        except ParamValidationError as e:
            raise ValidationError('Wrong source bucket name. %s' % e)

    def save(self, *args, **kwargs):
        if not self.source_data:
            self.source_data = {'nr_keys': 0, 'last_fetch': ''}
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
            tasks = generate_comparison_tasks_from_keys(keys)
        else:
            tasks = keys
        self.tasks = tasks
        self.source_data['nr_keys'] = len(keys)
        self.source_data['last_fetch'] = timezone.now().isoformat()
        self.save()

    @property
    def is_done(self) -> bool:
        return self.labels.count() >= self.nr_required_labels

    @property
    def nr_required_labels(self) -> int:
        return len(self.tasks) * self.min_labels_per_key

    def is_user_authorised_to_contribute(self, user: User) -> bool:
        if self.is_public:
            return True
        elif user.is_anonymous:
            return False
        else:
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
        return self.users.annotate(nr_labels=Count('labels', filter=Q(labels__dataset=self))
                                   ).filter(nr_labels__gt=0).order_by('nr_labels')

    @property
    def invite_link(self):
        return reverse('signup_with_invite', args=[str(self.invite_key)])


class Label(models.Model):
    class Meta:
        db_table = 'Label'

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='labels')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='labels')
    task = models.CharField(max_length=128)
    data = JSONField()
    action = models.CharField(choices=LabelActionType.choices(), max_length=64)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=254, blank=False, null=False)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    Profile.objects.get_or_create(user=instance)
    instance.profile.save()
