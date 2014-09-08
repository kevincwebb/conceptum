from django import forms
from ranking.models import RankingProcess

# this may seem superfluous now, but in the future if/when we support
# more exotic kinds of ranking, as well as voting deadlines, it will
# be useful for an admin to set these things in advance
class RankingProcessSetupForm(forms.ModelForm):
    class Meta:
        model = RankingProcess
        fields = ['value_choices']

class BinaryChoiceForm(forms.Form):
    final_choices = forms.ModelMultipleChoiceField(
        queryset=ConceptAtom.objects.none(),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):

        node = kwargs.pop('node')
        
        super(CreateMergeForm, self).__init__(*args, **kwargs)
        
        #self.fields['final_choices'].queryset = 

    

        
