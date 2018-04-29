from django.db.models import ExpressionWrapper, F, Count, QuerySet, FloatField
from django.db.models.functions import Cast


def annotate_datasets_for_view(datasets: QuerySet):
    annotated = datasets.extra(select={'nr_source_keys': 'cardinality(source_keys)'}).annotate(nr_labels=Count('label'))
    annotated = annotated.annotate(
        submitted_keys=ExpressionWrapper(F('nr_labels') / Cast(F('min_labels_per_key'), FloatField()),
                                         output_field=FloatField())
    )
    annotated = annotated.values('id', 'title', 'description', 'nr_labels', 'nr_source_keys', 'submitted_keys',
                                 'labeling_approach', 'min_labels_per_key')
    return annotated
