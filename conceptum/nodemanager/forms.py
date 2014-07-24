from django import forms
from django.forms.formsets import formset_factory

from nodemanager.models import ConceptAtom

class AtomForm(forms.ModelForm):

    pk = forms.IntegerField(widget=forms.HiddenInput(attrs={'readonly': True}),
                      required=False)

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

class CreateMergeForm(forms.Form):

    free_atoms = forms.ModelMultipleChoiceField(
        queryset=ConceptAtom.get_unmerged_atoms(),
        widget=forms.CheckboxSelectMultiple,
    )
    merged_atoms = forms.ModelChoiceField(
        queryset=ConceptAtom.get_merge_top_level_atoms(),
        widget=forms.RadioSelect,
        required=False
    )
    new_atom_name = forms.CharField(max_length=140, required=False)
