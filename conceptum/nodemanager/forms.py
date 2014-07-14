from django.forms import ModelForm
from nodemanager.models import ConceptAtom

class AtomForm(ModelForm):

    class Meta:
        model = ConceptAtom
        fields = ['text']
