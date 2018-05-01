import logging
import uuid
from typing import List

import boto3
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from django.utils import timezone

from data_model.enums import AwsRegionType, LabelingApproachEnum
from kono_data.utils import get_s3_bucket_from_aws_arn

logger = logging.getLogger(__name__)


class Dataset(models.Model):
    class Meta:
        db_table = 'Dataset'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source_uri = models.CharField(blank=False, null=False, max_length=128,
                                  help_text='Give Amazon Resource Name (ARN), e.g.: "arn:aws:s3:::test-kono-data"')
    source_region = models.CharField(choices=AwsRegionType.choices(),
                                     default=AwsRegionType.eu_west_1,
                                     max_length=16,
                                     help_text='Give the AWS region of the S3 bucket. Required to show the content')
    is_public = models.BooleanField(default=False)
    title = models.CharField(max_length=140, blank=False, null=False, help_text='Give your dataset a descriptive title')
    description = models.TextField(max_length=1000, help_text='Additional information about your dataset')
    labeling_approach = models.CharField(choices=LabelingApproachEnum.choices(),
                                         default=LabelingApproachEnum.width_first,
                                         max_length=16,
                                         help_text='Choose a labeling approaching. This influences which keys are shown '
                                                   'to your users first. Only revelant if min_labels_per_key is larger than 1.'
                                                   'Width first: get a label for every key first and then reach the minimum labels per key.'
                                                   'Depth first: get the minimum labels per key first and then continue to other keys.')
    min_labels_per_key = models.PositiveSmallIntegerField(default=1,
                                                          help_text='How many labels should be saved for each key')
    possible_labels = ArrayField(
        models.CharField(max_length=128, blank=False),
        help_text='Give a comma-separated list of the labels in your dataset. Example: "hotdog, not hotdog"'
    )
    source_data = JSONField(null=True, blank=True,
                            help_text='Keys in your dataset, will be automatically fetched and overwritten each time you save.')
    admins = models.ManyToManyField(User, related_name='admin_datasets', blank=True)
    contributors = models.ManyToManyField(User, related_name='contributor_datasets', blank=True)

    def __str__(self):
        return f'{self.user} - {self.source_region} - {self.source_uri} - public: {self.is_public}'

    def save(self, *args, **kwargs):
        self.fetch_keys_from_source()
        super(Dataset, self).save(*args, **kwargs)

    def fetch_keys_from_source(self):
        bucket_name = get_s3_bucket_from_aws_arn(str(self.source_uri))
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

        self.source_data['keys'] = keys
        self.source_data['nr_keys'] = len(keys)
        self.source_data['last_fetch'] = timezone.now().isoformat()

    @property
    def source_keys(self):
        return self.source_data['keys']

    @property
    def is_done(self) -> bool:
        return self.labels.count() >= self.nr_required_labels

    @property
    def nr_required_labels(self) -> int:
        return len(self.source_keys) * self.min_labels_per_key


class Label(models.Model):
    class Meta:
        db_table = 'Label'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='labels')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='labels')
    key = models.CharField(max_length=64, null=True)
    data = JSONField()


def get_unprocessed_keys(user: User, dataset: Dataset, n: int) -> List:
    if user.is_anonymous:
        return []

    labels = user.labels.values_list('key', flat=True)
    unprocessed_keys = set(dataset.source_keys) - set(labels)
    return list(unprocessed_keys)


def get_unprocessed_key(user: User, dataset: Dataset):
    unprocessed_keys = get_unprocessed_keys(user, dataset, n=1)
    return unprocessed_keys[0] if unprocessed_keys else None
