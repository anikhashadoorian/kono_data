from django.contrib import admin
from django.forms import ModelForm

from data_model.models import Dataset, Label

from prettyjson import PrettyJSONWidget


class JsonForm(ModelForm):
    class Meta:
        model = Dataset
        fields = '__all__'
        widgets = {
            'source_data': PrettyJSONWidget(attrs={'initial': 'parsed'}),
        }


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    form = JsonForm


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    pass
