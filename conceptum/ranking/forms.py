from django import forms
from django.contrib.contenttypes.models import ContentType

from ranking.models import RankingProcess
from nodemanager.models import ConceptNode, ConceptAtom

### For some reason imports weren't working so this re-declaration is
### a crufty workaround

#given a model, return its ContenType (needed for generic keys
#declared in ranking app models)
def get_ct(model):
    return ContentType.objects.get_for_model(model)

#given a node, get the ranking process attached to it (via generic query)
def get_ranking_process(node):
    return RankingProcess.objects.filter(object_id=node.id,
                                         content_type=get_ct(node)).get()


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
        
        node_id = kwargs.pop('node_id')
        node = ConceptNode.objects.filter(pk=node_id).get()
        ranking_process = get_ranking_process(node)
        super(BinaryChoiceForm, self).__init__(*args, **kwargs)

        # This is needed because there's no way we can return a
        # QUERYSET of things from get_rank_choices without losing
        # generality. We right now have a list of the things, and we
        # need to convert it to a queryset, since this is the only
        # type (to my knowledge) that the 'queryset' field of a form
        # field will accept. Thus, we get each atom's id and search
        # for them all again, except this time they are returned as a
        # queryset.
        atom_ids = map(lambda obj: obj.id, ranking_process.get_rank_choices())
        atom_qset = ConceptAtom.objects.filter(pk__in=atom_ids)
        self.fields['final_choices'].queryset = atom_qset
