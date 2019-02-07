from django import forms
from django.utils.safestring import mark_safe
from .models import NodeGroup


class ConfigForm(forms.Form):
    file = forms.FileField(label='Config File (.ini)',
            help_text=mark_safe('Sample configuration can be found '
                      r'<a href="/nodeConfigs/logman_sample.ini">here</a>.'))

    nodes = forms.ModelMultipleChoiceField(
            queryset=NodeGroup.objects.all(),
            label='Choose Nodes',
            help_text='Hold CTRL and choose the nodes to apply this config to.')

    def __init__(self, groupID, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nodes'].queryset = NodeGroup.objects\
            .get(id=groupID).nodes.all()
