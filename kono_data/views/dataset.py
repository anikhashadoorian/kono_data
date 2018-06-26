import tempfile

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.text import slugify

from data_model.export_models import ExportModel
from data_model.models import Dataset, Label
from data_model.utils import annotate_datasets_for_view, annotate_dataset_for_view
from kono_data.forms import DatasetForm
from kono_data.settings import NR_USERS_IN_LEADERBOARD


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
    context = {'form': form, 'dataset': dataset,
               'is_edit': dataset_id is not None}
    return render(request, "create_dataset.html", context)


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
        datasets = Dataset.objects.none()

    context['datasets'] = annotate_datasets_for_view(datasets, user)

    return render(request, "datasets.html", context)


def show_leaderboard(request, **kwargs):
    dataset_id = kwargs.get('dataset')
    dataset = Dataset.objects.filter(id=dataset_id).first()
    users = dataset.get_leaderboard_users()[:NR_USERS_IN_LEADERBOARD]
    context = {'dataset': annotate_dataset_for_view(dataset, request.user), 'users': users}
    return render(request, "leaderboard.html", context)
