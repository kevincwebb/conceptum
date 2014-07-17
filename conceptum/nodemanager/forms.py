from django.forms import ModelForm
from django.forms.formsets import formset_factory

from nodemanager.models import ConceptAtom

class AtomForm(ModelForm):

    class Meta:
        model = ConceptAtom
        fields = ['text']

    def clean_text(self):
        data = self.cleaned_data['text']
        if not data:
            raise forms.ValidationError("Can't have an empty Concept Atom!")

        return data

AtomFormSet = formset_factory(AtomForm)
