from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
#from django.contrib import messages
#from django.contrib.contenttypes.models import ContentType

# <<<<<<< HEAD
# from .models import Interview, Excerpt, get_concept_list, ConceptExcerpt, TopicTag
#=======
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
     
           
                
# class MultiTagField(forms.Field):
#     """
#     Field to collect email addresses as one large text input, where addresses are
#     seperated by semi-colon. After processing, the data is accessed as an array
#     of email strings.
#     """
#     def to_python(self, value):
#         """
#         Normalize data to a list of strings.
#         """
#         if not value:
#             return []
#         value = ''.join(value.split()) #remove whitespace
#         strings = value.split(";")
#         if '' in strings:
#             strings.remove('') #in case there was a trailing ';'
#         return strings
# 
# 
# 
# 
# class ConceptInterviewAddForm(forms.ModelForm):
#     class Meta:
#         model = Interview
#         fields = ['interviewee','date_of_interview']
#         widgets = {
#             'date_of_interview': forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}),
#         }
# 
#     def __init__(self, *args, **kwargs):
#         """
#         This method creates text field for each concept returned by the imported
#         function get_concept_list().
#         
#         If kwarg 'group' is None, then there is a field to select an interview group.
#         If 'group' is not None, then there is no field for interview group, and the
#         provided group is automatically saved to the model.
#         """
#         super(ConceptInterviewAddForm, self).__init__(*args, **kwargs)
#         
#             
#     def save(self, request):
#         """
#         Saves an interview.  The request argument provides access to request.user,
#         which is used for the uuploaded_by field. If an excerpt response field is
#         left blank, that excerpt will not be created.
#         """
#         i = Interview()
#         i.interviewee = self.cleaned_data.get('interviewee')
#         i.date_of_interview =  self.cleaned_data.get('date_of_interview')
#         i.uploaded_by = User.objects.get(pk=request.user.id)
#         i.save()
#     
#         return i
#     
#     
# class ConceptExcerptAddForm(forms.ModelForm):
#     """
#     Form for adding an excerpt
#     """
#     
#     topic_tags = MultiTagField(required=False,
#                                  widget=forms.Textarea(attrs={
#                                  'placeholder':"seperate with semicolons... \n\nTag 1;\nTag 2"}))
#     
#     class Meta:
#         model = ConceptExcerpt
#         #TODO: ability level and importance ranking (5 star rating system)
#         fields = ['concept_tag', 'response', 'topic_tags', 'ability_level', 'importance']
#         widgets = {
#             'concept_tag': forms.TextInput(attrs={'size': '60'})}
#     
#     def __init__(self, *args, **kwargs):
#         """
#         This method creates text field for each option.
#         MAX_CHOICES determines how many choices are available.
#         Empty choice fields will not be saved. 
#         """
#         super(ConceptExcerptAddForm, self).__init__(*args, **kwargs)
#         # self.fields["interview"]
#         # self.fields["correct"] = forms.ChoiceField(label=_("Correct Choice"),
#         #                                            choices=self.choices())
# 
# 
#   DO WE EVEN NEED THIS? we just need edit forms for the excerpts
# class ConceptInterviewEditForm(forms.ModelForm):
#     class Meta:
#         model = Interview
#         fields = ['interviewee','date_of_interview']
#     
#     def __init__(self, *args, **kwargs):
#         """
#         This method creates text field for each concept returned by the imported
#         function get_concept_list().  The interview's old response is used as
#         initial data.
#         """
#         super(ConceptInterviewEditForm, self).__init__(*args, **kwargs)
#         
#     
#     def save(self):
#         """
#         Saves an updated interview.  Since initial values are used for all form fields,
#         all model fields are updated and saved.  If an excerpt response field is left blank,
#         that excerpt will not be created or will be deleted if it previously existed.
#         """
#         i = self.instance # the interview
#         i.interviewee = self.cleaned_data.get('interviewee')
#         i.date_of_interview =  self.cleaned_data.get('date_of_interview')
#         i.save()


# class ConceptExcerptEditForm(forms.ModelForm):
#     topic_tags = MultiTagField(required=False,
#                                  widget=forms.Textarea(attrs={
#                                  'placeholder':"seperate with semicolons... \n\nTag 1;\nTag 2"}))

#     class Meta:
#         model = ConceptExcerpt
#         #maybe topic_tags should be topictag_set
#         fields = ['concept_tag', 'response', 'ability_level', 'importance']
#     
#     def __init__(self, *args, **kwargs):
#         """
#         This method creates text field for each concept returned by the imported
#         function get_concept_list().  The interview's old response is used as
#         initial data.
#         """
#         super(ConceptExcerptEditForm, self).__init__(*args, **kwargs)
#
#           #set up something for topic_tags here
#           
#         
#     
#     def save(self):
#         """
#         Saves an updated interview.  Since initial values are used for all form fields,
#         all model fields are updated and saved.  If an excerpt response field is left blank,
#         that excerpt will not be created or will be deleted if it previously existed.
#         """
#         i = self.instance # the interview
#         i.concept_tag = self.cleaned_data.get('concept_tag')
#         i.response =  self.cleaned_data.get('response')
#         i.ability_level = self.cleaned_data.get('ability_level')
#         i.importance = self.cleaned_data.get('importance')
#         i.save()


        