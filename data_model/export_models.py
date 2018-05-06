import csv

OUTDATED_KEYS = 'outdated_keys'


class ExportModel(object):
    @staticmethod
    def as_csv(file, queryset):
        """
        'file' (string: absolute path),
        'queryset' a Django QuerySet instance,
        'fields' a list or tuple of field model field names (strings)
        :returns (string) path to file
        """
        fields = ['key', 'user_id'] + queryset.first().dataset.possible_labels + [OUTDATED_KEYS]
        nr_fields = len(fields)
        outdated_keys_index = fields.index(OUTDATED_KEYS)
        with open(file, 'w+') as f:
            writer = csv.writer(f)
            writer.writerow(fields)
            for obj in queryset:
                if not obj.key:
                    continue

                row = [''] * nr_fields
                row[0] = obj.key
                row[1] = obj.user.id
                row[outdated_keys_index] = {}

                for k, v in obj.data.items():
                    try:
                        row[fields.index(k)] = v
                    except ValueError:
                        row[outdated_keys_index][k] = v

                row = list(map(lambda x: x if x != "" else False, row))
                writer.writerow(row)
            path = f.name
        return path
