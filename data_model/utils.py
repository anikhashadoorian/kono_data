from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db.models import ExpressionWrapper, F, Count, QuerySet, FloatField
from django.db.models.functions import Cast


def annotate_datasets_for_view(datasets: QuerySet):
    annotated = datasets.annotate(nr_source_keys=KeyTextTransform('nr_keys', 'source_data'),
                                  nr_labels=Count('labels'))
    annotated = annotated.annotate(
        processed_percentage=ExpressionWrapper(100 * F('nr_labels') /
                                               Cast(F('min_labels_per_key'), FloatField()) /
                                               Cast(F('nr_source_keys'), FloatField()),
                                               output_field=FloatField()))
    annotated = annotated.values('id', 'title', 'description', 'nr_labels', 'nr_source_keys',
                                 'labeling_approach', 'min_labels_per_key', 'processed_percentage')
    return annotated
