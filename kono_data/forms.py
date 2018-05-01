from django import forms


class ProcessForm(forms.Form):
    def __init__(self, *args, **kwargs):
        labels = kwargs.pop('labels')
        super(ProcessForm, self).__init__(*args, **kwargs)
        self.generate_fields_for_labels(labels)

    def generate_fields_for_labels(self, labels):
        for i, question in enumerate(labels):
            self.fields[question] = forms.BooleanField(label=question,
                                                       required=False,
                                                       initial=False,
                                                       )
