from django import forms
from django.forms import ModelForm
from django.utils.html import escape

from data_model.models import Dataset

class ProcessForm(forms.Form):
    def __init__(self, *args, **kwargs):
        labels = kwargs.pop('labels')
        super(ProcessForm, self).__init__(*args, **kwargs)
        self.generate_fields_for_labels(labels)

    def generate_fields_for_labels(self, labels):
        for i, label in enumerate(labels):
            widget = forms.CheckboxInput(
                attrs={'accesskey': str(i + 1), 'id': f'label_select_{i+1}'})
            label_str = f'{i+1}: {label}' if i < 10 else label
            self.fields[label] = forms.BooleanField(label=label_str, required=False, initial=False, widget=widget)


class DatasetForm(ModelForm):
    class Meta:
        model = Dataset
        exclude = ['user', 'source_data', 'labeling_approach', 'admins', 'contributors']
        labels = {
            'source_uri': 'AWS S3 Bucket',
        }
        help_texts = {
            'source_uri': 'Give your AWS S3 bucket name, e.g. ',
        }

    def __init__(self, *args, **kwargs):
        super(DatasetForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            label = self.fields[field].label or str(field)
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover',
                     'data-content': escape(help_text),
                     'data-placement': 'right',
                     'data-container': 'body',
                     'data-trigger': 'hover',
                     'title': label
                     })
