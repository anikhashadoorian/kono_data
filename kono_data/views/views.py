import logging

from django.views.generic import TemplateView

from data_model.models import Dataset
from data_model.utils import annotate_datasets_for_view

logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        datasets = Dataset.objects.filter(is_public=True).order_by('-id')
        context['datasets'] = annotate_datasets_for_view(datasets, context['view'].request.user)[:10]
        return context
