import tempfile

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.text import slugify

from data_model.export.dataset_export_models import RawDatasetExport, ProcessedDatasetExport, DatasetExport
from data_model.models import Dataset
from data_model.utils import annotate_datasets_for_view, annotate_dataset_for_view
from kono_data.forms import DatasetForm
from kono_data.settings import USERS_VISIBLE_ON_LEADERBOARD
from kono_data.utils import timing


@timing
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
            dataset.save()

            if request.POST.get('submit') == 'save_and_fetch':
                dataset.fetch_keys_from_source()
                return redirect('process', dataset=dataset.pk)
            else:
                return redirect('index')
    else:
        form = DatasetForm(instance=dataset)
        dataset = annotate_datasets_for_view(datasets, request.user).first()
    context = {'form': form, 'dataset': dataset,
               'is_edit': dataset_id is not None}
    return render(request, "create_dataset.html", context)


@timing
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


@timing
def export_dataset(request, **kwargs):
    user = request.user
    dataset_id = kwargs.get('dataset')
    export_type = kwargs.get('export_type')

    if export_type not in DatasetExport.SUPPORTED_EXPORT_MODELS:
        messages.info(request, f'Export type {export_type} is not supported for this dataset')
        return redirect('index')

    dataset = Dataset.objects.filter(id=dataset_id).first()
    if not dataset.is_user_authorised_admin(user):
        messages.error(request, 'You\'re not authorized to export this dataset =(')
        return redirect('index')

    if not dataset.labels.exists():
        messages.info(request, 'There are no labels for this dataset yet. Start processing first')
        return redirect('index')

    with tempfile.NamedTemporaryFile() as f:
        if export_type == 'raw':
            RawDatasetExport.as_csv(f.name, dataset)
        elif export_type == 'processed':
            ProcessedDatasetExport.as_csv(f.name, dataset)
        else:
            messages.error(request, 'Invalid export type selected for ')
            return redirect('index')

        response = HttpResponse(f.read(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(slugify(dataset))
    return response


@timing
def index_dataset(request, **kwargs):
    context = {}
    dataset_type = kwargs.get('type')
    context['type'] = dataset_type
    user = request.user
    datasets = Dataset.objects.none()
    if dataset_type == 'public':
        datasets = Dataset.objects.filter(is_public=True)
    elif not user.is_anonymous:
        datasets = Dataset.objects.exclude(is_public=True).filter(
            Q(user=user) | Q(admins__id=user.id) | Q(contributors__id=user.id)).distinct()

    context['datasets'] = annotate_datasets_for_view(datasets, user)

    return render(request, "datasets.html", context)


@timing
def show_leaderboard(request, **kwargs):
    dataset_id = kwargs.get('dataset')
    dataset = Dataset.objects.filter(id=dataset_id).first()
    users = dataset.get_leaderboard_users()[:USERS_VISIBLE_ON_LEADERBOARD]
    unique_files_compared = len(dataset.get_unique_processed_files())

    context = {'dataset': annotate_dataset_for_view(dataset, request.user),
               'users': users,
               'unique_files_compared': unique_files_compared}
    return render(request, "leaderboard.html", context)
