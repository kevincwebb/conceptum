from datetime import timedelta, datetime, date, time

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.validators import validate_email, ValidationError
from django.db import models

from interviews.models import get_concept_list, DummyConcept as Concept #TEMPORARY: DummyConcept
from .models import ExamResponse, FreeResponseQuestion, MultipleChoiceQuestion, \
                    MultipleChoiceOption, ResponseSet


NUM_CHOICES = 6 ####Max number of muliple choice choices
MAX_EMAILS = 30

class MultiEmailField(forms.Field):
    """
    Field to collect email addresses as one large text input, where addresses are
    seperated by semi-colon.  Used in DistributeFrom
    """
    def to_python(self, value):
        """
        Normalize data to a list of strings.
        """
        if not value:
            return []
        value = ''.join(value.split()) #remove whitespace
        strings = value.split(";")
        if '' in strings:
            strings.remove('') #in case there was a trailing ';'
        return strings

    def validate(self, value):
        """
        Check if value consists only of valid emails.
        """
        super(MultiEmailField, self).validate(value)
        for email in value:
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError("One or more email addresses is invalid.")

class ExamResponseChoiceField(forms.ModelMultipleChoiceField):
    """
    A custom field used in DistributeForm so that the list of pending exams (for re-sending)
    displays the respondent's email.
    """
    def label_from_instance(self, obj):
        return obj.respondent


class SelectConceptForm(forms.ModelForm):
    """
    A form for selecting a concept
    """
    class Meta:
        model = Concept
        exclude = ['name']
    concept = forms.ModelChoiceField(queryset=get_concept_list(),
                               to_field_name="name", )



class AddFreeResponseForm(forms.ModelForm):
    """
    Form for adding a free response questions
    """
    question = models.CharField(blank = False)
   
    class Meta:
        model = FreeResponseQuestion
        fields = ['question' ]
        widgets = {
            'question': forms.TextInput(attrs={'size': '60'})}

    # I suspect that this method is never called... -Ben
    #def form_valid(self, form):
    #    s, created = Exam.objects.get_or_create(name=survey.views.SURVEY_NAME)
    #    q = FreeResponseQuestion(exam = s,
    #                             question = self.cleaned_data.get('question'))
    

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
    #def form_valid(self):
    #    #s, created = Exam.objects.get_or_create(name=survey.views.SURVEY_NAME)
    #    q = MultipleChoiceQuestion(exam = s, question = self.cleaned_data.get('question'),
    #                               content_type = self.instance.content_type,
    #                               object_id = self.instance.object_id)
    #    q.save()
    #    self.set_choices(q)
    #    
    #def set_choices(self, q):
    #    for x in range(1, NUM_CHOICES+1):
    #        choice_text = self.cleaned_data.get("choice_%d" % x)
    #        if (choice_text):
    #            c = MultipleChoiceOption(question = q, text = choice_text)
    #            c.save()


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
        return self.instance


class NewResponseSetForm(forms.ModelForm):
    class Meta:
        model = ResponseSet
        fields = ['course', 'pre_test'] #'modules' ]
        
        #widgets = {
        #    'modules': forms.CheckboxSelectMultiple(),
        #}

class DistributeForm(forms.Form):
    
    expiration_date = forms.DateField(initial= (date.today() + timedelta(days=7)),
                                      help_text='YYYY-MM-DD')
    
    expiration_time = forms.TimeField(initial= time(23,59,59),
                                      help_text='HH:MM:SS  (use 24-hr clock)')
    
    recipients = MultiEmailField(required=False,
                                 widget=forms.Textarea(attrs={
                                 'placeholder':"seperate with semicolons... \n\nemail1@email.com;\nemail2@email.com"}))
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super(DistributeForm, self).__init__(*args, **kwargs)
        pending_exams = self.instance.examresponse_set.filter(submitted__exact=None)
        self.fields["resend"] = ExamResponseChoiceField(queryset=pending_exams,
                                                        required=False,
                                                        widget=forms.CheckboxSelectMultiple())
    
    def clean_recipients(self):
        """
        Check that there has not already been an exam sent to this address. Note that this
        does not check that an email has not been entered twice in the same input.
        """
        data = self.cleaned_data['recipients']
        for email in data:
            if self.instance.examresponse_set.filter(respondent__exact=email):
                raise forms.ValidationError("You have already sent an exam to one or more \
                                            of these addresses.  If you'd like to resend an \
                                            exam, use the checkbox below.")
        return data
    
    def clean(self):
        """
        Check that expiration time is in the future and no more than 100 days from today
        """
        cleaned_data = super(DistributeForm, self).clean()
        expiration_date = cleaned_data.get("expiration_date")
        expiration_time = cleaned_data.get("expiration_time")

        if expiration_date and expiration_time:
            expiration_datetime = datetime.combine(expiration_date, expiration_time)
            if datetime.today() + timedelta(days=100) < expiration_datetime:
                raise forms.ValidationError("Expiration date/time cannot be more than 100 days after today")
            if datetime.today() >= expiration_datetime:
                raise forms.ValidationError("Expiration date/time must be in future")
        return cleaned_data


class BlankForm(forms.Form):
    class Meta:
        fields = []

    
class ExamResponseForm(forms.ModelForm):
    class Meta:
        model = ExamResponse
        fields = []
        
    def __init__(self, *args, **kwargs):
        super(ExamResponseForm, self).__init__(*args, **kwargs) 
        for response in self.instance.freeresponseresponse_set.all():
            self.fields["FR_response_%d" % response.id] = \
                forms.CharField(label=_(response.question.__unicode__()),
                                required=True,
                                widget=forms.Textarea(),)
        for response in self.instance.multiplechoiceresponse_set.all():
            self.fields["MC_response_%d" % response.id] = \
                forms.ModelChoiceField(label=_(response.question.__unicode__()),
                                       required=True,
                                       queryset=response.question.multiplechoiceoption_set.all(),
                                       empty_label=None,
                                       widget=forms.RadioSelect())
            
    def save(self):
        for response in self.instance.freeresponseresponse_set.all():
            response.response = self.cleaned_data.get("FR_response_%d" % response.id)
            response.save()
        for response in self.instance.multiplechoiceresponse_set.all():
            response.option = self.cleaned_data.get("MC_response_%d" % response.id)
            response.save()