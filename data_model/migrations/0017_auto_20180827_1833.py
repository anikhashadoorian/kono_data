# Generated by Django 2.1 on 2018-08-27 18:33

import markdownx.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_model', '0016_label_loading_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='description',
            field=markdownx.models.MarkdownxField(help_text='Additional information about your dataset'),
        ),
    ]
