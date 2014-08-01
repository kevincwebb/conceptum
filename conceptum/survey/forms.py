from django import forms, utils
from django.db import models
from django.forms import ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from django.contrib.contenttypes.models import ContentType, ContentTypeManager

from exam.models import Exam, FreeResponseQuestion, FreeResponseResponse, MultipleChoiceQuestion, MultipleChoiceOption, MultipleChoiceResponse
from interviews.models import get_concept_list, DummyConcept as Concept

#number of muliple choice choices
NUM_CHOICES = 6;

User = get_user_model()

class SelectConceptForm(forms.ModelForm):
    class Meta:
        model = Concept
        exclude = ['name']
    concept = ModelChoiceField(queryset=get_concept_list(),
                               to_field_name="name", )
    
class AddFreeResponseForm(forms.ModelForm):
    question = models.CharField(blank = False)
   
    class Meta:
        model = FreeResponseQuestion
        fields = ['question' ]

    def form_valid(self, form):
        s, created = Exam.objects.get_or_create(name='Survey')
        q = FreeResponseQuestion(exam = s,
                                 question = self.cleaned_data.get('question'))
    

class AddMultipleChoiceForm(forms.ModelForm):
    class Meta:
        model = MultipleChoiceQuestion
        fields = ['question',]
        
    question = forms.CharField(label = 'Question')
    
    def __init__(self, *args, **kwargs):
        """
        This method creates text field for each option.
        NUM_CHOICES determines how many choices are available.
        Empty choice fields will not be saved. 
        """
        super(AddMultipleChoiceForm, self).__init__(*args, **kwargs)
        for x in range(1, NUM_CHOICES+1):
            self.fields["choice_%d" % x] = \
                forms.CharField(label=_("choice %s" % x),
                                required=False,)

    def form_valid(self):
        s, created = Exam.objects.get_or_create(name='Survey')
        q = self.instance
        q.exam = s
        q.question = self.cleaned_data.get('question')
        q.id = self.instance.object_id
        
        for x in range(1, NUM_CHOICES+1):
            choice_text = self.cleaned_data.get("choice_%d" % x)
            if (choice_text):
                c = MultipleChoiceOption(question = q, text = choice_text)
                c.save()


class MultipleChoiceEditForm(forms.ModelForm):
    
    class Meta:
        model = MultipleChoiceQuestion
        fields = ['question']
        
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
            #finds the current largest MultipleChoiceOption id number and sets the new one to 1 greater
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
        q = self.instance # the interview
        q.question = self.cleaned_data.get('question')
        q.save()
        
        if (self.NEW_ID > -1):
            if(self.cleaned_data.get("choice_%d" % self.NEW_ID) ):
                choice_text = self.cleaned_data.get("choice_%d" % self.NEW_ID)
                if (choice_text):
                    c = MultipleChoiceOption(question = q, text = choice_text)
                    c.save()
        for choice in MultipleChoiceOption.objects.filter():
            if(choice.question == self.instance):
                text = self.cleaned_data.get("choice_%d" % choice.id)
                if text:
                    choice.text = text
                    choice.save()
                else:
                    choice.delete()
    