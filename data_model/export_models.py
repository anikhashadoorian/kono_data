import csv


class ExportModel(object):
    @staticmethod
    def as_csv(file, queryset):
        """
        'file' (string: absolute path),
        'queryset' a Django QuerySet instance,
        'fields' a list or tuple of field model field names (strings)
        :returns (string) path to file
        """
        fields = ['key', 'user_id'] + queryset.first().dataset.possible_labels
        nr_fields = len(fields)
        with open(file, 'w+') as f:
            writer = csv.writer(f)
            writer.writerow(fields)
            for obj in queryset:
                if not obj.key:
                    continue

                row = [''] * nr_fields
                row[0] = obj.key
                row[1] = obj.user.id

                for k, v in obj.data.items():
                    row[fields.index(k)] = v

                writer.writerow(row)
            path = f.name
        return path
