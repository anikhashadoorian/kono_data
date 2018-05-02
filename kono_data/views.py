import logging
import tempfile
from urllib.parse import quote

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.text import slugify
from django.views.generic import TemplateView

from data_model.export_models import ExportModel
from data_model.models import Dataset, get_unprocessed_key, Label
from data_model.utils import annotate_datasets_for_view
from kono_data.forms import ProcessForm
from kono_data.utils import get_s3_bucket_from_aws_arn

logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        datasets = Dataset.objects.filter(is_public=True).order_by('-id')
        context['datasets'] = annotate_datasets_for_view(datasets)[:10]
        return context


def process(request, **kwargs):
    context = {}

    user = request.user
    dataset_id = kwargs.get('dataset')
    dataset = Dataset.objects.filter(id=dataset_id).first()

    if not dataset.is_user_authorised_to_process(user):
        messages.error(request, 'You\'re not authorized to process this dataset =(')
        return redirect('index')

    form = ProcessForm(request.POST or None, labels=dataset.possible_labels)

    if form.is_valid():
        if user.is_anonymous:
            messages.add_message(request, 10, 'Sign up or Login to label and use your data')
        else:
            key = form.data.get('key')
            Label.objects.create(user=user, dataset=dataset, key=key, data=form.cleaned_data)
        return redirect("process", dataset=dataset_id)

    context['form'] = form
    context['dataset'] = dataset
    bucket = get_s3_bucket_from_aws_arn(dataset.source_uri)
    key = get_unprocessed_key(user, dataset)

    if key:
        encoded_key = quote(key)
        context['key'] = key
        context['key_src'] = f'https://s3-{dataset.source_region}.amazonaws.com/{bucket}/{encoded_key}'

    return render(request, "process.html", context)


def show_dataset(request, **kwargs):
    dataset_id = kwargs.get('dataset')
    datasets = Dataset.objects.filter(id=dataset_id)
    dataset = datasets.first()

    if not dataset.is_user_authorised_to_process(request.user):
        messages.error(request, 'You\'re not authorized to view this dataset =(')
        return redirect('index')

    is_user_authorised_to_export = dataset.is_user_authorised_to_export(request.user)
    context = {'dataset': annotate_datasets_for_view(datasets).first(),
               'is_user_authorised_to_export': is_user_authorised_to_export}
    return render(request, "show_dataset.html", context)


def export_dataset(request, **kwargs):
    user = request.user
    dataset_id = kwargs.get('dataset')
    dataset = Dataset.objects.filter(id=dataset_id).first()

    if not dataset.is_user_authorised_to_export(user):
        messages.error(request, 'You\'re not authorized to export this dataset =(')
        return redirect('index')

    queryset = Label.objects.filter(dataset=dataset)
    with tempfile.NamedTemporaryFile() as f:
        ExportModel.as_csv(f.name, queryset)
        response = HttpResponse(f.read(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(slugify(dataset))
    return response


def index_dataset(request, **kwargs):
    context = {}
    type = kwargs.get('type')
    context['type'] = type
    user = request.user
    if type == 'public':
        datasets = Dataset.objects.filter(is_public=True)
    elif not user.is_anonymous:
        datasets = Dataset.objects.filter(Q(is_public=False) &
                                          (Q(user=user) | Q(admins__id=user.id) | Q(contributors__id=user.id)))
    else:
        datasets = []

    context['datasets'] = annotate_datasets_for_view(datasets)

    return render(request, "datasets.html", context)
