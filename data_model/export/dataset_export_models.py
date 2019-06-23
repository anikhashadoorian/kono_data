import csv
from abc import abstractmethod

from data_model.export.export_utils import get_scores_from_labels

from django.db.models import Func, F, Value


class DatasetExport:
    SUPPORTED_EXPORT_MODELS = ['raw', 'processed']
    OUTDATED_KEYS = 'outdated_keys'

    @classmethod
    @abstractmethod
    def as_csv(cls, file, dataset):
        raise NotImplementedError


class RawDatasetExport(DatasetExport):
    @classmethod
    def as_csv(cls, file, dataset):
        """
        'file' (string: absolute path),
        'queryset' a Django QuerySet instance,
        'fields' a list or tuple of field model field names (strings)
        :returns (string) path to file
        """
        fields = ['task', 'user_id', 'processing_time', 'loading_time'] + dataset.label_names + [cls.OUTDATED_KEYS]
        nr_fields = len(fields)
        outdated_tasks_index = fields.index(cls.OUTDATED_KEYS)
        with open(file, 'w+') as f:
            writer = csv.writer(f)
            writer.writerow(fields)
            for obj in dataset.labels:
                if not obj.task:
                    continue

                row = [''] * nr_fields
                row[0] = obj.task
                row[1] = obj.user.id
                row[outdated_tasks_index] = {}

                for k, v in obj.data.items():
                    try:
                        row[fields.index(k)] = v
                    except ValueError:
                        row[outdated_tasks_index][k] = v

                row = list(map(lambda x: x if x != "" else None, row))
                writer.writerow(row)
            path = f.name
        return path


class ProcessedDatasetExport(DatasetExport):
    @classmethod
    def as_csv(cls, file, dataset):
        """
        'file' (string: absolute path),
        'queryset' a Django QuerySet instance,
        'fields' a list or tuple of field model field names (strings)
        :returns (string) path to file
        """
        label_names = dataset.label_names
        label_field_tuples = [(f'score_{label}',
                               f'normalised_score_{label}',
                               f'confidence_{label}') for label in label_names]
        column_names = list(sum(label_field_tuples, ()))

        annotated_labels = dataset.labels.annotate(
            key1=Func(F('task__definition'), Value(','), Value(1), function='split_part'),
            key2=Func(F('task__definition'), Value(','), Value(2), function='split_part'))

        unique_keys = list(dataset.get_unique_processed_files())

        label_name_to_scores = {label_name: get_scores_from_labels(annotated_labels, unique_keys, label_name)
                                for label_name in label_names}

        fields = ['key'] + column_names
        with open(file, 'w+') as f:
            writer = csv.writer(f)
            writer.writerow(fields)
            for key in unique_keys:
                row = [key]
                score_tuples = [(label_name_to_scores[label_name][key].score,
                                 label_name_to_scores[label_name][key].normalised_score,
                                 label_name_to_scores[label_name][key].rating.sigma) for label_name in label_names]
                row += list(sum(score_tuples, ()))
                writer.writerow(row)
            path = f.name
        return path
