# Generated by Django 2.1.7 on 2019-03-24 10:56

from django.db import migrations, models
import django.db.models.deletion
import uuid


def creates_tasks_from_dataset_array_field(apps, schema_editor):
    # Dataset = apps.get_model("data_model", "Dataset")
    Label = apps.get_model("data_model", "Label")
    Task = apps.get_model("data_model", "Task")

    for label in Label.objects.all():
        task, updated = Task.objects.update_or_create(definition=label.task)
        task.save()
        label.task_external = task
        label.save()


class Migration(migrations.Migration):
    dependencies = [
        ('data_model', '0018_auto_20180915_1855'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('definition', models.CharField(max_length=256)),
            ],
            options={
                'db_table': 'Task',
            },
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='labels_per_key',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='tasks',
        ),
        migrations.AddField(
            model_name='dataset',
            name='labels_per_task',
            field=models.PositiveSmallIntegerField(default=1,
                                                   help_text='How many labels should be saved for each task'),
        ),
        migrations.AddField(
            model_name='label',
            name='task_external',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks',
                                    to='data_model.Task', null=True),
        ),
        migrations.RunPython(
            creates_tasks_from_dataset_array_field
        ),
    ]
