from django import forms
from django.forms.formsets import formset_factory, BaseFormSet
from authtools.models import User

from nodemanager.models import CITreeInfo

class Stage1SetupForm(forms.Form):
    """
    This form is used when the Stage 1 process is first created to
    establish the parameters of the concept hierarchy.
    """
    admins = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_superuser=True),
        widget=forms.CheckboxSelectMultiple,
    )

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
