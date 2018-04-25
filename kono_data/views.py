from django.http import HttpResponse
from django.views.generic import TemplateView

from data_model.models import Dataset, get_unprocessed_key
from kono_data.utils import get_s3_bucket_from_aws_arn


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def process(request):
    return HttpResponse("")


class ProcessView(TemplateView):
    template_name = "process.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dataset = Dataset.objects.first()
        key = get_unprocessed_key(self.request.user, dataset)
        bucket = get_s3_bucket_from_aws_arn(dataset.source_uri)
        context['key'] = key
        context['key_src'] = f'https://s3-{dataset.source_region}.amazonaws.com/{bucket}/{key}'
        context['labels'] = dataset.possible_labels
        return context
