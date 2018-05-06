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
from kono_data.forms import ProcessForm, DatasetForm
from kono_data.utils import get_s3_bucket_from_str

logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        datasets = Dataset.objects.filter(is_public=True).order_by('-id')
        context['datasets'] = annotate_datasets_for_view(datasets, context['view'].request.user)[:10]
        return context


def process(request, **kwargs):
    context = {}

    user = request.user
    dataset_id = kwargs.get('dataset')
    dataset = Dataset.objects.filter(id=dataset_id).first()

    if not dataset.is_user_authorised_to_contribute(user):
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
    if not dataset.source_keys:
        if dataset.is_user_authorised_admin(user):
            messages.info(request, f'Dataset "{dataset}" has no keys. Fetch new data to start processing')
            return redirect("update_or_create_dataset", dataset=dataset_id)
        else:
            messages.info(request, f'Dataset "{dataset}" has no keys. Ask your admin to fetch data to start processing')
            return redirect("index")

    key = get_unprocessed_key(user, dataset)
    if key:
        encoded_key = quote(key)
        bucket = get_s3_bucket_from_str(dataset.source_uri)
        context['key'] = key
        context['key_src'] = f'https://s3-{dataset.source_region}.amazonaws.com/{bucket}/{encoded_key}'

    return render(request, "process.html", context)


def update_or_create_dataset(request, **kwargs):
    dataset_id = kwargs.get('dataset')
    datasets = Dataset.objects.filter(id=dataset_id)
    dataset = datasets.first()

    if dataset and not dataset.is_user_authorised_admin(request.user):
        messages.error(request, 'You\'re not authorized to edit this dataset =(')
        return redirect('index')

    if request.method == "POST":
        form = DatasetForm(request.POST, instance=dataset)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.user = request.user

            if request.POST.get('submit') == 'save_and_fetch':
                dataset.fetch_keys_from_source()
                return redirect('process', dataset=dataset.pk)
            else:
                dataset.save()
                return redirect('index')
    else:
        form = DatasetForm(instance=dataset)
        dataset = annotate_datasets_for_view(datasets, request.user).first()

    return render(request, "create_dataset.html",
                  {'form': form, 'dataset': dataset,
                   'is_edit': dataset_id is not None})


def fetch_dataset_from_source(request, **kwargs):
    dataset_id = kwargs.get('dataset')
    dataset = Dataset.objects.filter(id=dataset_id).first()

    if dataset.is_user_authorised_admin(request.user):
        dataset.fetch_keys_from_source()
        messages.success(request, 'Dataset updated successfully! 🎉')
        return redirect('update_or_create_dataset', dataset=dataset_id)
    else:
        messages.error(request, 'You\'re not authorized to edit this dataset =(')
        return redirect('index')


def export_dataset(request, **kwargs):
    user = request.user
    dataset_id = kwargs.get('dataset')
    dataset = Dataset.objects.filter(id=dataset_id).first()

    if not dataset.is_user_authorised_admin(user):
        messages.error(request, 'You\'re not authorized to export this dataset =(')
        return redirect('index')

    queryset = Label.objects.filter(dataset=dataset)
    if not queryset.exists():
        messages.info(request, 'There are no labels for this dataset yet. Start processing first')
        return redirect('index')

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

    context['datasets'] = annotate_datasets_for_view(datasets, user)

    return render(request, "datasets.html", context)
