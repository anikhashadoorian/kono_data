from django import forms


class ProcessForm(forms.Form):
    def __init__(self, *args, **kwargs):
        extra = kwargs.pop('extra')
        super(ProcessForm, self).__init__(*args, **kwargs)

        for i, question in enumerate(extra):
            self.fields[question] = forms.BooleanField(label=question,
                                                       required=False,
                                                       initial=False)
