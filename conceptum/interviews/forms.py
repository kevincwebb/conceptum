import logging

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
#from django.contrib import messages

from .models import Interview, Excerpt, get_concept_list

User = get_user_model()
logger = logging.getLogger(__name__)

class AddForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['interviewee','date_of_interview']

    def __init__(self, *args, **kwargs):
        super(AddForm, self).__init__(*args, **kwargs)
        for concept in get_concept_list():
            # TODO: when get_concept_list is fixed, we may need to update this line
            self.fields["response_%d" % concept.id] = \
                forms.CharField(label=_("%s response" % concept),
                                required=False,
                                widget=forms.Textarea())
            
    def save(self, request):        
        i = Interview()
        i.interviewee = self.cleaned_data.get('interviewee')
        i.date_of_interview =  self.cleaned_data.get('date_of_interview')
        i.uploaded_by = User.objects.get(pk=request.user.id)
        i.save()
        
        for concept in get_concept_list():
            # TODO: when get_concept_list is fixed, may need to update this line
            response = self.cleaned_data.get("response_%d" % concept.id)
            # if a response was left blank, an Excerpt is not created
            if response:
                e = Excerpt()
                e.content_topic = concept
                e.interview = i
                e.response = response
                e.save()
        return i

class EditForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['interviewee','date_of_interview']
    
    def __init__(self, *args, **kwargs):
        super(EditForm, self).__init__(*args, **kwargs) 
        for concept in get_concept_list():
            # TODO: when get_concept_list is fixed, we may need to update this line
            initial_response = ""
            if self.instance.excerpt_set.filter(topic_id=concept.id):
                initial_response = self.instance.excerpt_set.get(topic_id=concept.id).response
            self.fields["response_%d" % concept.id] = \
                forms.CharField(label=_("%s response" % concept),
                                required=False,
                                widget=forms.Textarea(),
                                initial=initial_response )
    
    def save(self):
        i = self.instance
        i.interviewee = self.cleaned_data.get('interviewee')
        i.date_of_interview =  self.cleaned_data.get('date_of_interview')
        i.save()
        for concept in get_concept_list():
            # TODO: when get_concept_list is fixed, may need to update this line
            response = self.cleaned_data.get("response_%d" % concept.id)
            if i.excerpt_set.filter(topic_id=concept.id):
                e = i.excerpt_set.get(topic_id=concept.id)
                if response:
                    e.content_topic = concept
                    e.interview = self.instance
                    e.response = response
                    e.save()
                else:
                    e.delete()
            elif response:
                e = Excerpt()
                e.content_topic = concept
                e.interview = i
                e.response = response
                e.save()
        