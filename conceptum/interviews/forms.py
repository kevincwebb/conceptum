from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
#from django.contrib import messages
#from django.contrib.contenttypes.models import ContentType

from .models import InterviewGroup, Interview, Excerpt, get_concept_list

User = get_user_model()


class AddForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['interviewee','date_of_interview']
        widgets = {
            'date_of_interview': forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}),
        }

    def __init__(self, *args, **kwargs):
        """
        This method creates text field for each concept returned by the imported
        function get_concept_list().
        
        If kwarg 'group' is None, then there is a field to select an interview group.
        If 'group' is not None, then there is no field for interview group, and the
        provided group is automatically saved to the model.
        """
        self.group = kwargs.pop('group')
        super(AddForm, self).__init__(*args, **kwargs)
        if not self.group:
            self.fields["group"] = forms.ModelChoiceField(
                queryset=InterviewGroup.objects.filter(unlocked=True))
        for concept in get_concept_list():
            # TODO: when get_concept_list is fixed, we may need to update this line
            self.fields["response_%d" % concept.id] = \
                forms.CharField(label=_("%s response" % concept),
                                required=False,
                                widget=forms.Textarea())
            
    def save(self, request):
        """
        Saves an interview.  The request argument provides access to request.user,
        which is used for the uuploaded_by field. If an excerpt response field is
        left blank, that excerpt will not be created.
        """
        i = Interview()
        i.interviewee = self.cleaned_data.get('interviewee')
        i.date_of_interview =  self.cleaned_data.get('date_of_interview')
        i.uploaded_by = User.objects.get(pk=request.user.id)
        if self.group:
            i.group = self.group
        else:
            i.group = self.cleaned_data.get('group')
        i.save()
        
        for concept in get_concept_list():
            # TODO: when get_concept_list is fixed, may need to update this line
            response = self.cleaned_data.get("response_%d" % concept.id)
            # if a response was left blank, an Excerpt is not created
            if response:
                e = Excerpt()
                e.content_object = concept
                e.interview = i
                e.response = response
                e.save()
        return i

class EditForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['interviewee','date_of_interview']
    
    def __init__(self, *args, **kwargs):
        """
        This method creates text field for each concept returned by the imported
        function get_concept_list().  The interview's old response is used as
        initial data.
        """
        super(EditForm, self).__init__(*args, **kwargs)        
        for concept in get_concept_list():         
            self.fields["response_%d" % concept.id] = \
                forms.CharField(label=_("%s response" % concept),
                                required=False,
                                widget=forms.Textarea(),)
                                #initial=initial_response )
    
    def save(self):
        """
        Saves an updated interview.  Since initial values are used for all form fields,
        all model fields are updated and saved.  If an excerpt response field is left blank,
        that excerpt will not be created or will be deleted if it previously existed.
        """
        i = self.instance # the interview
        i.interviewee = self.cleaned_data.get('interviewee')
        i.date_of_interview =  self.cleaned_data.get('date_of_interview')
        i.save()
        for concept in get_concept_list():
            # TODO: when get_concept_list is fixed, may need to update this line
            response = self.cleaned_data.get("response_%d" % concept.id)
            if i.excerpt_set.filter(object_id=concept.id):
                e = i.excerpt_set.get(object_id=concept.id)
                if response:
                    e.content_object = concept
                    e.interview = self.instance
                    e.response = response
                    e.save()
                else:
                    e.delete()
            elif response:
                e = Excerpt()
                e.content_object = concept
                e.interview = i
                e.response = response
                e.save()
        