# Generated by Django 2.1 on 2018-09-15 18:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_model', '0017_auto_20180827_1833'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataset',
            old_name='possible_labels',
            new_name='label_names',
        ),
        migrations.RenameField(
            model_name='dataset',
            old_name='min_labels_per_key',
            new_name='labels_per_key',
        ),
    ]
