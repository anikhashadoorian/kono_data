from django import forms

from data_model.enums import TaskType


class SingleImageLabelForm(forms.Form):
    def __init__(self, *args, **kwargs):
        labels = kwargs.pop('labels')
        super(SingleImageLabelForm, self).__init__(*args, **kwargs)
        self.generate_fields_for_labels(labels)

    def generate_fields_for_labels(self, labels):
        for i, label in enumerate(labels):
            widget = forms.CheckboxInput(
                attrs={'accesskey': str(i + 1), 'id': f'label_select_{i+1}'})
            label_str = f'{i+1}: {label}' if i < 10 else label
            self.fields[label] = forms.BooleanField(label=label_str, required=False, initial=False, widget=widget)


class TwoImageComparisonForm(forms.Form):
    def __init__(self, *args, **kwargs):
        labels = kwargs.pop('labels')
        super(TwoImageComparisonForm, self).__init__(*args, **kwargs)


task_type_to_process_form = {
    TaskType.single_image_label.value: SingleImageLabelForm,
    TaskType.two_image_comparison.value: TwoImageComparisonForm

}
