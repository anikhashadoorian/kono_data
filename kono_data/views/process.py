from urllib.parse import quote

from django.contrib import messages
from django.shortcuts import redirect, render

from data_model.models import Dataset, Label
from data_model.utils import get_unprocessed_key
from kono_data.forms import ProcessForm
from kono_data.utils import get_s3_bucket_from_str


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
            messages.info(request, 'Sign up or Login to label this dataset')
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