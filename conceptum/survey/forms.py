from django import forms, utils
from django.db import models
from django.forms import ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from django.contrib.contenttypes.models import ContentType, ContentTypeManager

from exam.models import Exam, FreeResponseQuestion, FreeResponseResponse, MultipleChoiceQuestion, MultipleChoiceOption, MultipleChoiceResponse
from interviews.models import get_concept_list, DummyConcept as Concept
import survey.views
import reversion


####Max number of muliple choice choices
NUM_CHOICES = 6;


class SelectConceptForm(forms.ModelForm):
    """
    A form for selecting a concept
    """
    class Meta:
        model = Concept
        exclude = ['name']
    concept = ModelChoiceField(queryset=get_concept_list(),
                               to_field_name="name", )

    
class AddFreeResponseForm(forms.ModelForm):
    """
    Form for adding a free response question
    """
    question = models.CharField(blank = False)
   
    class Meta:
        model = FreeResponseQuestion
        fields = ['question' ]
        widgets = {
            'question': forms.TextInput(attrs={'size': '60'})}

    # I suspect that this method is never called... -Ben
    def form_valid(self, form):
        s, created = Exam.objects.get_or_create(name=survey.views.SURVEY_NAME)
        q = FreeResponseQuestion(exam = s,
                                 question = self.cleaned_data.get('question'))
    

class AddMultipleChoiceForm(forms.ModelForm):
    """
    Form for adding a multiple choice question
    """
    class Meta:
        model = MultipleChoiceQuestion
        fields = ['question',]
        widgets = {
            'question': forms.TextInput(attrs={'size': '60'})}
    
    def __init__(self, *args, **kwargs):
        """
        This method creates text field for each option.
        NUM_CHOICES determines how many choices are available.
        Empty choice fields will not be saved. 
        """
        super(AddMultipleChoiceForm, self).__init__(*args, **kwargs)
        #variable x enumerates the choices
        for x in range(1, NUM_CHOICES+1):
            self.fields["choice_%d" % x] = \
                forms.CharField(label=_("choice %s" % x),
                                required=False,)


    def clean(self):
        cleaned_data = super(AddMultipleChoiceForm, self).clean()
        choice_counter = 0
        for x in range(1, NUM_CHOICES+1):
            choice = self.cleaned_data.get("choice_%d" % x)
            if choice:
                choice_counter = choice_counter + 1
        if choice_counter < 1:
            raise forms.ValidationError("You need to provide Choices for the Multiple Choice Question", code = 'no_choices')
        return cleaned_data
            
    # This method could be moved to the view, using form.cleaned_data
    # Then we would not need to import survey.views
    def form_valid(self):
        s, created = Exam.objects.get_or_create(name=survey.views.SURVEY_NAME)
        q = MultipleChoiceQuestion(exam = s, question = self.cleaned_data.get('question'),
                                   content_type = self.instance.content_type,
                                   object_id = self.instance.object_id)
        q.save()
        self.set_choices(q)
        
        
    def set_choices(self, q):
        for x in range(1, NUM_CHOICES+1):
            choice_text = self.cleaned_data.get("choice_%d" % x)
            if (choice_text):
                c = MultipleChoiceOption(question = q, text = choice_text)
                c.save()


class MultipleChoiceEditForm(forms.ModelForm):
    """
    Form for editing a multiple choice question. If there are less than NUM_CHOICES choices,
    there is an extra field to add a new choice. If a choice's text is deleted and the form
    is submitted, that choice will be deleted. 
    """
    class Meta:
        model = MultipleChoiceQuestion
        fields = ['question']
        widgets = {
            'question': forms.TextInput(attrs={'size': '60'})}
        
    NEW_ID = -1
    
    def __init__(self, *args, **kwargs):
        """
        This method creates text field for each choice.  The choice's text value is used as
        initial data.
        Creates extra field for adding a new choice. 
        """
        
        super(MultipleChoiceEditForm, self).__init__(*args, **kwargs)
        
        i = 1
        for choice in MultipleChoiceOption.objects.all():
            if(choice.question.id == self.instance.id):
                self.fields["choice_%d" % choice.id] = \
                    forms.CharField(label=_("choice %s" % i),
                                    required=False,)
                i = i + 1
        
        if(i <= NUM_CHOICES):
            #finds the current largest MultipleChoiceOption id number and
            #sets NEW_ID to 1 greater.(the newly created MultipleChoiceOption's id = NEW_ID in save()
            max_id = MultipleChoiceOption.objects.all().order_by("-id")[0].id
            new_id = max_id + 1
            self.NEW_ID = new_id
            self.fields["choice_%d" % new_id] = \
                        forms.CharField(label=_("Add A Choice:"),
                                        required=False,)
        
  
    def save(self):
        """
        Saves the updated choices. If a choice field is left blank,
        that choice will be deleted if it previously existed.
        Creates a new multiplechoiceoption if add_choice_feild is not empty
        """
        q = self.instance # the question
        q.question = self.cleaned_data.get('question')
       
        
        if (self.NEW_ID > -1):
            if(self.cleaned_data.get("choice_%d" % self.NEW_ID) ):
                choice_text = self.cleaned_data.get("choice_%d" % self.NEW_ID)
                if (choice_text):
                    c = MultipleChoiceOption(question = q, text = choice_text)
                    c.save()
        #checks to see if each choice still has text in the field, will change if edited,
        #and delete choice if field is blank
        for choice in MultipleChoiceOption.objects.all():
            if(choice.question == self.instance):
                text = self.cleaned_data.get("choice_%d" % choice.id)
                if text:
                    if(choice.text != text):
                        c = MultipleChoiceOption(question = q, text = text)
                        c.save()
                        choice.delete()
                else:
                    choice.delete()
        q.save()
    