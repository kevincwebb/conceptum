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
        queryset=ConceptAtom.get_final_atoms(),
        widget=forms.RadioSelect,
        required=False
    )
    new_atom_name = forms.CharField(max_length=140, required=False)

    new_merge_id = 'new merge'
    edit_merge_id = 'edit merge'

    def clean(self):

        cleaned_data = super(CreateMergeForm, self).clean()
        new_atom_name = cleaned_data.get('new_atom_name')
        merged_atom_choice = cleaned_data.get('merged_atoms')

        if (new_atom_name and merged_atom_choice):
            raise forms.ValidationError("Must either pick or create an atom to merge, cannot do both.")
        elif (not new_atom_name and not merged_atom_choice):
            raise forms.ValidationError("Must pick or create an atom to merge with, none entered.")

        return cleaned_data
