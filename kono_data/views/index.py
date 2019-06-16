import logging

from django.views.generic import TemplateView

from data_model.models import Dataset
from data_model.utils import annotate_datasets_for_view
from kono_data.settings import DATASETS_ON_INDEX_PAGE
from kono_data.utils import timing

logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = "index.html"

    @timing
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_anonymous:
            datasets = Dataset.objects.filter(is_public=True).order_by('-id')
        else:
            datasets = (
                    Dataset.objects.filter(is_public=True) | user.owner_datasets.all() |
                    user.admin_datasets.all() | user.contributor_datasets.all()
            ).distinct().all()
        context['datasets'] = annotate_datasets_for_view(datasets, user, DATASETS_ON_INDEX_PAGE)
        return context
