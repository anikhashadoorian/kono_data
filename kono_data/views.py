from django.contrib import messages
from django.db.models import Count, F, IntegerField, Sum, ExpressionWrapper, DecimalField
from django.db.models.functions import Length
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from data_model.models import Dataset, get_unprocessed_key, Label
from data_model.utils import annotate_datasets_for_view
from kono_data.forms import ProcessForm
from kono_data.utils import get_s3_bucket_from_aws_arn


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        datasets = Dataset.objects.filter(is_public=True).order_by('-id')
        context['datasets'] = annotate_datasets_for_view(datasets)[:10]
        return context


def process(request, **kwargs):
    context = {}
    dataset_id = kwargs.get('dataset')

    dataset = Dataset.objects.filter(id=dataset_id).first()
    form = ProcessForm(request.POST or None, extra=dataset.possible_labels)
    if form.is_valid():
        # do_something_with(form.cleaned_data)
        # save label here
        if request.user.is_anonymous:
            messages.add_message(request, 10, 'Sign up or Login to label and use your data')
        else:
            key = form.data.get('key')
            Label.objects.create(user=request.user, dataset=dataset, key=key, data=form.cleaned_data)
        return redirect("process", dataset=dataset_id)

    if not dataset_id:
        messages.add_message(request, 10, 'Trying to process an unknown dataset. Return to home page')
    else:
        context['form'] = form
        key = get_unprocessed_key(request.user, dataset)
        bucket = get_s3_bucket_from_aws_arn(dataset.source_uri)
        context['dataset'] = dataset
        context['key'] = key
        context['key_src'] = f'https://s3-{dataset.source_region}.amazonaws.com/{bucket}/{key}'
        context['labels'] = dataset.possible_labels

    return render(request, "process.html", context)


def show_dataset(request, **kwargs):
    dataset_id = kwargs.get('dataset')
    dataset = Dataset.objects.filter(id=dataset_id)
    context = {}
    context['dataset'] = annotate_datasets_for_view(dataset).first()
    return render(request, "show_dataset.html", context)


from django.db.models import Aggregate


class SumCardinality(Aggregate):
    template = 'SUM(CARDINALITY(%(expressions)s))'


def index_dataset(request, **kwargs):
    context = {}
    type = kwargs.get('type')
    context['type'] = type
    if type == 'public':
        datasets = Dataset.objects.filter(is_public=True)
    elif not request.user.is_anonymous:
        datasets = Dataset.objects.filter(is_public=False, user=request.user)
    else:
        datasets = []

    context['datasets'] = annotate_datasets_for_view(datasets)

    return render(request, "datasets.html", context)
