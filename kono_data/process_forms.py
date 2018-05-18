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
        self.generate_fields_for_labels(labels)

    def generate_fields_for_labels(self, labels):
        for i, label in enumerate(labels):
            label_str = f'{i+1}: {label}' if i < 10 else label
            widget = forms.CheckboxInput(
                attrs={'accesskey': str(i + 1), 'id': f'label_select_{i+1}',
                       'type': 'checkbox', 'class': 'checkbox', 'data-toggle': 'toggle',
                       'data-on': 'right',
                       'data-off': 'left'})
            self.fields[label] = forms.BooleanField(label=label_str, required=False, initial=False, widget=widget)
        self.add_confirmation_checkbox()

    def add_confirmation_checkbox(self):
        index = 0
        label_str = f'{index}: Confirm'
        widget = forms.CheckboxInput(
            attrs={'accesskey': str(index), 'id': f'label_select_{index}',
                   'type': 'checkbox', 'class': 'checkbox', 'data-toggle': 'toggle',
                   'data-on': 'confirm', 'data-off': 'not confirmed',
                   'data-onstyle': 'success', 'data-offstyle': 'danger',
                   'onchange': "validate_save_button()"})
        self.fields['confirm'] = forms.BooleanField(label=label_str, required=True, initial=False, widget=widget)


task_type_to_process_form = {
    TaskType.single_image_label.value: SingleImageLabelForm,
    TaskType.two_image_comparison.value: TwoImageComparisonForm

}
