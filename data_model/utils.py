from typing import Optional

from django.contrib.auth.models import User
from django.contrib.postgres.aggregates import BitOr
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db.models import ExpressionWrapper, F, Count, QuerySet, FloatField, Q, When, BooleanField, Case
from django.db.models.functions import Cast, Greatest


def annotate_datasets_for_view(datasets: QuerySet, user: Optional[User] = None):
    annotated = datasets.annotate(
        nr_source_keys=Greatest(Cast(KeyTextTransform('nr_keys', 'source_data'), FloatField()), 1.0),
        nr_labels=Greatest(Count('labels'), 0.0))
    annotated = annotated.annotate(
        processed_percentage=ExpressionWrapper(100 * F('nr_labels') /
                                               Cast(F('min_labels_per_key'), FloatField()) /
                                               F('nr_source_keys'),
                                               output_field=FloatField()))
    annotated_fields = ['id', 'title', 'description', 'nr_labels', 'nr_source_keys',
                        'labeling_approach', 'min_labels_per_key', 'processed_percentage']
    if user:
        if user.is_anonymous:
            annotated = annotated.annotate(
                is_user_authorised_to_contribute=F('is_public'))
            annotated_fields += ['is_user_authorised_to_contribute']
        else:
            annotated = annotated.annotate(
                is_user_authorised_admin=Case(
                    When(Q(user=user) | Q(admins__id=user.id) | Q(contributors__id=user.id), then=True),
                    default=False, output_field=BooleanField()))
            annotated = annotated.annotate(
                is_user_authorised_to_contribute=Case(When(Q(is_public=True) | Q(is_user_authorised_admin=True),
                                                           then=True),
                                                      default=False, output_field=BooleanField()))
            annotated_fields += ['is_user_authorised_admin', 'is_user_authorised_to_contribute']

    return annotated.values(*annotated_fields)
