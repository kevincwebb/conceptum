from django import forms
from django.forms.formsets import formset_factory, BaseFormSet
from authtools.models import User

from nodemanager.models import CITreeInfo

class Stage1Configure(forms.Form):
    """
    This form is used when the Stage 1 process is first created to
    establish the parameters of the concept hierarchy.
    """
    root_name = forms.CharField(
        label = 'Root node name',
        help_text = 'The name you\'d like to assign to the root of your concept tree.',
        initial = 'CI Root'
    )

    child_typename = forms.CharField(
        label = 'Child type',
        help_text = 'What you would like to call child node(s) of the root (this is only a label for humans to read).',
        initial = 'module',
        max_length = 50
    )

    max_children = forms.IntegerField(
        label = 'Maximum children',
        help_text = 'What is the maximum number of child nodes that any CI contributer should be allowed to propose?',
        min_value = 1,
    )
