# Generated by Django 2.0.4 on 2018-05-01 08:45

import data_model.enums
from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('source_uri', models.CharField(help_text='Give Amazon Resource Name (ARN), e.g.: "arn:aws:s3:::test-kono-data"', max_length=128)),
                ('source_region', models.CharField(choices=[('eu-central-1', 'eu-central-1'), ('eu-west-1', 'eu-west-1')], default=data_model.enums.AwsRegionType('eu-west-1'), help_text='Give the AWS region of the S3 bucket. Required to show the content', max_length=16)),
                ('is_public', models.BooleanField(default=False)),
                ('title', models.CharField(help_text='Give your dataset a descriptive title', max_length=140)),
                ('description', models.TextField(help_text='Additional information about your dataset', max_length=1000)),
                ('min_labels_per_key', models.PositiveSmallIntegerField(default=1, help_text='How many labels should be saved for each key')),
                ('possible_labels', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=128), help_text='Give a comma-separated list of the labels in your dataset. Example: "hotdog, not hotdog"', size=None)),
                ('source_data', django.contrib.postgres.fields.jsonb.JSONField(help_text='Keys in your dataset, will be automatically fetched and overwritten each time you save.')),
                ('admins', models.ManyToManyField(blank=True, related_name='admin_datasets', to=settings.AUTH_USER_MODEL)),
                ('contributors', models.ManyToManyField(blank=True, related_name='contributor_datasets', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Dataset',
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=64, null=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='labels', to='data_model.Dataset')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='labels', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Label',
            },
        ),
    ]
