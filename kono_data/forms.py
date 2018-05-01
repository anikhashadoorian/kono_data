from django import forms


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
