import logging

from django.db.models import Q
from django.views.generic import TemplateView

from data_model.models import Dataset
from data_model.utils import annotate_datasets_for_view

logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_anonymous:
            datasets = Dataset.objects.filter(is_public=True).order_by('-id')
        else:
            user = self.request.user
            datasets = Dataset.objects.filter(Q(is_public=True) |
                                              (Q(user=user) | Q(admins__id=user.id) | Q(contributors__id=user.id)))
        context['datasets'] = annotate_datasets_for_view(datasets, context['view'].request.user)[:10]
        return context
