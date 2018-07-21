from html import unescape

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.utils.html import strip_tags

from data_model.models import Dataset


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
                     'data-content': unescape(help_text),
                     'data-placement': 'right',
                     'data-container': 'body',
                     'data-trigger': 'hover',
                     'title': label
                     })


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter valid email address')
    bio = forms.CharField(max_length=500, required=False)
    location = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'location', 'bio')
        labels = {
            'bio': 'TEST',
        }
        help_texts = {
            'location': 'Let us know where on this beautiful earth you are right now',
            'bio': 'Tell us a little bit about yourself'
        }

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            help_text = self.fields[field].help_text
            label = self.fields[field].label or str(field)
            if help_text != '':
                self.fields[field].widget.attrs.update(
                    {'class': 'has-popover',
                     'data-content': strip_tags(help_text).replace('&#39;', '\''),
                     'data-placement': 'right',
                     'data-container': 'body',
                     'data-trigger': 'hover',
                     'title': label
                     })
