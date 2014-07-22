from django.forms import ModelForm, HiddenInput, IntegerField
from django.forms.formsets import formset_factory
#from django.forms.extras.widgets import HiddenInput

from nodemanager.models import ConceptAtom

class AtomForm(ModelForm):

    pk = IntegerField(widget=HiddenInput(attrs={'readonly': True}))

    class Meta:
        model = ConceptAtom
        fields = ['text']

    def clean_text(self):
        data = self.cleaned_data['text']
        if not data:
            raise forms.ValidationError("Can't have an empty Concept Atom!")

        return data

AtomFormSet = formset_factory(AtomForm,
                              can_delete=True,
                              extra=5,)
