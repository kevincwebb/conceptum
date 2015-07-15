from datetime import timedelta, datetime, date, time

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.validators import validate_email, ValidationError
from django.db import models, transaction

from interviews.models import get_concept_list, DummyConcept as Concept #TEMPORARY: DummyConcept
from .models import ExamResponse, FreeResponseQuestion, MultipleChoiceQuestion, \
                    Question, MultipleChoiceOption, ResponseSet, Exam, \
                    MAX_CHOICES, REQUIRED_CHOICES
import reversion

MAX_EMAILS = 30 # I don't think this is currently checked

class MultiEmailField(forms.Field):
    """
    Field to collect email addresses as one large text input, where addresses are
    seperated by semi-colon. After processing, the data is accessed as an array
    of email strings.
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


class SelectConceptForm(forms.Form):
    """
    A form for selecting a concept
    """
    concept = forms.ModelChoiceField(queryset=get_concept_list(),
                                     to_field_name="name", )


class AddFreeResponseForm(forms.ModelForm):
    """
    Form for adding a free response questions
    """
    question = models.CharField(blank = False)
   
    class Meta:
        model = FreeResponseQuestion
        fields = ['question','image']
        widgets = {'question': forms.TextInput(attrs={'size': '60'})}
    

class AddMultipleChoiceForm(forms.ModelForm):
    """
    Form for adding a multiple choice question
    """
    class Meta:
        model = MultipleChoiceQuestion
        fields = ['question','image']
        widgets = {
            'question': forms.TextInput(attrs={'size': '60'})}
    
    def choices(self):
        l = [('','---')]
        for i in range(1,MAX_CHOICES+1):
            l.append((i,i))
        return l
    
    def __init__(self, *args, **kwargs):
        """
        This method creates text field for each option.
        MAX_CHOICES determines how many choices are available.
        Empty choice fields will not be saved. 
        """
        super(AddMultipleChoiceForm, self).__init__(*args, **kwargs)
        self.fields["correct"] = forms.ChoiceField(label=_("Correct Choice"),
                                                   choices=self.choices())
        # Create fields for choices: choice_1, choice_2,...
        for x in range(1, MAX_CHOICES+1):
            self.fields["choice_%d" % x] = forms.CharField(label=_("choice %s" % x),
                                                           required=False,)

    def clean(self):
        cleaned_data = super(AddMultipleChoiceForm, self).clean()
        
        # Consolidate choices so there are no holes
        choice_counter = 0
        for x in range(1, MAX_CHOICES+1):
            choice = self.cleaned_data.get("choice_%d" % x)
            if choice:
                self.cleaned_data["choice_%d" % x] = None
                choice_counter += 1
                self.cleaned_data["choice_%d" % choice_counter] = choice
                if self.cleaned_data.get("correct") == str(x):
                    self.cleaned_data["correct"] = choice_counter
        
        # Require at least REQUIRED_CHOICES choices
        if choice_counter < REQUIRED_CHOICES:
            raise forms.ValidationError("You must provide at least %d choice." % REQUIRED_CHOICES,
                                        code = 'no_choices')
        
        # Check for duplicates
        for i in range(1,choice_counter+1):
            for j in range(i+1, choice_counter+1):
                if (self.cleaned_data["choice_%d" % i]==self.cleaned_data["choice_%d" % j]):
                    raise forms.ValidationError("You have two identical choices.")
        
        # Make sure the designated correct choice is not blank
        if not self.cleaned_data.get("choice_%s" % self.cleaned_data.get("correct")):
            raise forms.ValidationError("The choice you marked correct is blank.")
        
        return cleaned_data


class MultipleChoiceEditForm(forms.ModelForm):
    """
    Form for editing a multiple choice question. If there are less than MAX_CHOICES choices,
    there is an extra field to add a new choice. If a choice's text is deleted and the form
    is submitted, that choice will be deleted.
    
    The view expects that the 3rd field is the forms.ChoiceField for marking a correct answer,
    followed by alternating choice and index fields.
    """
    class Meta:
        model = MultipleChoiceQuestion
        fields = ['question','image']
        widgets = {
            'question': forms.TextInput(attrs={'size': '60'})}
    
    def choices(self):
        l = []
        for option in self.instance.multiplechoiceoption_set.all():
            l.append((option.id,option.text))
        l.append((-1,"New choice"))
        return l
        
    def __init__(self, *args, **kwargs):
        """
        This method creates text field for each choice.  The choice's text value is used as
        initial data.
        Creates extra field for adding a new choice. 
        """    
        super(MultipleChoiceEditForm, self).__init__(*args, **kwargs)
        
        self.fields["correct"] = forms.ChoiceField(label=_("Correct Choice"),
                                                   choices=self.choices(),
                                                   initial=self.instance.correct_option.id,
                                                   widget=forms.RadioSelect)
        # Create fields for choices and indices
        # choice_1, index_1, choice_2, index_2, ...
        i = 1
        for choice in self.instance.multiplechoiceoption_set.all():
            self.fields["choice_%d" % choice.id] = forms.CharField(label=_("Choice"),
                                                                   required=False,
                                                                   initial=choice.text)
            self.fields["index_%d" % choice.id] = forms.IntegerField(label=_("Order"),
                                                                     required=False,
                                                                     initial=choice.index,
                                                                     validators=[
                                                                     MaxValueValidator(MAX_CHOICES),
                                                                     MinValueValidator(1)])
            i = i + 1
        if(i <= MAX_CHOICES):
            self.fields["choice_new"] = forms.CharField(label=_("Add A Choice:"), required=False)
            self.fields["index_new"] = forms.IntegerField(label=_("Order"), required=False)
        
    def clean(self):
        cleaned_data = super(MultipleChoiceEditForm, self).clean() 
        
        indices = []
        choice_counter = 0
        # Require that all non-blank choices have an index
        for choice in self.instance.multiplechoiceoption_set.all():
            if self.cleaned_data.get("choice_%d" % choice.id):
                if not self.cleaned_data.get("index_%d" % choice.id):
                    raise forms.ValidationError("Make sure all non-blank choices have an order.")
                indices.append(self.cleaned_data['index_%d' % choice.id])
                choice_counter += 1
            else:
                if self.cleaned_data.get("index_%d" % choice.id):
                    raise forms.ValidationError("Make sure all blank choices do not have an order.")
        if self.cleaned_data.get("choice_new"):
            if not self.cleaned_data.get("index_new"):
                raise forms.ValidationError("Make sure all non-blank choices have an order.")
            indices.append(self.cleaned_data['index_new'])
            choice_counter += 1
        else:
            if self.cleaned_data.get("index_new"):
                raise forms.ValidationError("Make sure all blank choices do not have an order.")
            
        # Require at least REQUIRED_CHOICES choices
        if choice_counter < REQUIRED_CHOICES:
            raise forms.ValidationError("You must provide at least %d choice." % REQUIRED_CHOICES,
                                        code = 'no_choices')
        
        # Check given indices, should begin at 1 and increment by 1
        indices.sort()
        for i in range(1, choice_counter+1):
            if i != indices.pop(0):
                raise forms.ValidationError("Order must begin with 1, with no doubles or gaps")

        # Check for duplicates
        options = [option.id for option in self.instance.multiplechoiceoption_set.all()]
        options.append("new")
        for i in range(0,len(options)):
            if self.cleaned_data.get('choice_%s' % options[i]):
                for j in range(i+1,len(options)):
                    if (self.cleaned_data.get("choice_%s" % options[i])==
                        self.cleaned_data.get("choice_%s" % options[j])):
                            raise forms.ValidationError("You have two identical choices.")
        
        # Make sure the designated correct choice is not blank
        if not self.cleaned_data.get("choice_%s" % self.cleaned_data.get("correct")):
            if not (self.cleaned_data.get("choice_new") and self.cleaned_data.get("correct")=='-1'):
                raise forms.ValidationError("The choice you marked correct is blank.")

        return cleaned_data

    @transaction.atomic()
    @reversion.create_revision()  
    def save(self):
        """
        Saves the question and all choices.
        Deletes a choice if its field is blank.
        Creates a new choice if 'new_choice' field is not blank.
        
        It is important to save this question and all its options, even if they are unchanged,
        so that they are included in the revision.
        """
        self.instance.question = self.cleaned_data.get('question')
        self.instance.image = self.cleaned_data.get('image')
        self.instance.save()
        
        for choice in self.instance.multiplechoiceoption_set.all():
            text = self.cleaned_data.get("choice_%d" % choice.id)
            if text:
                choice.is_correct = False
                if int(self.cleaned_data.get("correct")) == choice.id:
                    choice.is_correct = True
                choice.text = text
                choice.index = self.cleaned_data.get("index_%d" % choice.id)
                choice.save()
            else:
                # delete choice if field is blank
                choice.delete()
        
        # create a new option, if provided
        new_text = self.cleaned_data.get("choice_new")
        if (new_text):
            correct = False
            if int(self.cleaned_data.get("correct")) == -1:
                correct = True
            MultipleChoiceOption.objects.create(question=self.instance,
                                                text=new_text,
                                                index=self.cleaned_data.get("index_new"),
                                                is_correct=correct)
            
        return self.instance


class QuestionVersionForm(forms.ModelForm):
    
    def get_version_choices(self):
        """
        A list of tuples (i,question)
        
        i is the index in get_unique_versions() and question is the
        question text at that version
        """
        l = []
        i = 0
        for version in self.instance.get_unique_versions():
            l.append( (i,version.field_dict['question']))
            i+=1
        return l
    
    def __init__(self, *args, **kwargs):
        """
        There is one field, a list of tuples
        """
        super(QuestionVersionForm, self).__init__(*args, **kwargs)
        self.fields['version']=forms.ChoiceField(choices=self.get_version_choices(),
                                                 widget=forms.RadioSelect())


class FreeResponseVersionForm(QuestionVersionForm):
    class Meta:
        model = FreeResponseQuestion
        fields = []
    
    @transaction.atomic()
    @reversion.create_revision()
    def save(self):
        """
        The data saved in 'version' is an integer that is the selected version's index
        in get_unique_versions()
        """
        index = int(self.cleaned_data.get('version'))
        version_list = self.instance.get_unique_versions()
        version_list[index].revert()
        return self.instance

        
class MultipleChoiceVersionForm(QuestionVersionForm):
    class Meta:
        model = MultipleChoiceQuestion
        fields = []
    
    @transaction.atomic()
    @reversion.create_revision()
    def save(self):
        """
        The data saved in 'version' is an integer that is the selected version's index
        in get_unique_versions()
        """
        index = int(self.cleaned_data.get('version'))
        version_list = self.instance.get_unique_versions()
        revision = version_list[index].revision
        
        # We would like to just call `version_list[index].revision.revert(delete=True)`
        # but this does not work with proxy models. We call our own revert method instead.
        self.instance.revision_revert(revision)

        return self.instance


class FinalizeSelectForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = []
    
    def __init__(self, *args, **kwargs):
        super(FinalizeSelectForm, self).__init__(*args, **kwargs)
        self.fields['select_questions']=forms.ModelMultipleChoiceField(
            queryset=self.instance.question_set.all().order_by('object_id'),
            widget=forms.CheckboxSelectMultiple)


class FinalizeOrderForm(forms.Form):
    class Meta:
        fields = []
    
    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('selected_questions')
        super(FinalizeOrderForm, self).__init__(*args, **kwargs)
        for question in self.queryset:
            self.fields['question_%d'%question.id]=forms.IntegerField(
                label=question,
                validators=[MaxValueValidator(len(self.queryset)),
                            MinValueValidator(1)],
                widget=forms.TextInput(attrs={'size':2}))
    
    def clean(self):
        cleaned_data = super(FinalizeOrderForm, self).clean()
        used_numbers = []
        for question in self.queryset:
            number = self.cleaned_data.get('question_%d'%question.id)
            if used_numbers.count(number):
                raise ValidationError("Please assign numbers such that there are no duplicates.")
            else:
                if number in range(1, len(self.queryset)+1):
                # if the number isn't in this range, then it is a different validation error.
                    used_numbers.append(number)
            
        return cleaned_data


class FinalizeConfirmForm(forms.Form):
    """
    Blank form for the confirm page in our form wizard
    """
    pass


class NewResponseSetForm(forms.ModelForm):
    """
    Form in which a distributor provides course info and selects modules
    
    TODO: module selection field
    """
    class Meta:
        model = ResponseSet
        fields = ['course', 'pre_test'] #'modules' ]
        
        #widgets = {
        #    'modules': forms.CheckboxSelectMultiple(),
        #}


class DistributeForm(forms.Form):
    """
    Form for a distributor to provide an expiration date and time and a list of
    student emails.
    
    'recipients' is a custom field MultiEmailField that takes a long text input of emails
    seperated by semicolons and formats it as an array.
    
    'resend' is a custom field ExamResponseChoiceField that is effectively a ModelChoiceField.
    The choices for this field are ExamResponses (in this set) which have been previously
    sent out but have not yet been submitted.
    """
    
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


class CleanupForm(forms.Form):
    """
    A Blank Form
    """
    class Meta:
        fields = []

    
class ExamResponseForm(forms.ModelForm):
    """
    Has fields for every question in an exam.  These fields are generated in the __init__()
    method.  After an ExamResponse has been submitted, the save() method updates the
    FreeResponseResponse and QuestionResponseResponse objects with the student's responses.
    """
    class Meta:
        model = ExamResponse
        fields = []
        
    def __init__(self, *args, **kwargs):
        """
        Generate a field for each associated QuestionResponse object.
        """
        super(ExamResponseForm, self).__init__(*args, **kwargs)
        multiple_choice_responses = self.instance.multiplechoiceresponse_set.all()
        free_response_responses = self.instance.freeresponseresponse_set.all()
        
        # need to create response fields in the order that their questions are ordered
        for question in self.instance.response_set.exam.question_set.all():
            if question.is_multiple_choice:
                response = multiple_choice_responses.get(question=question)
                self.fields["MC_response_%d" % response.id] = forms.ModelChoiceField(
                    label=_(response.question.__unicode__()),
                    required=True,
                    queryset=response.question.multiplechoiceoption_set.all(),
                    empty_label=None,
                    widget=forms.RadioSelect())
            else:
                response = free_response_responses.get(question=question)
                self.fields["FR_response_%d" % response.id] = forms.CharField(
                    label=_(response.question.__unicode__()),
                    required=True,
                    widget=forms.Textarea(),)
        
        #for response in self.instance.freeresponseresponse_set.all():
        #    self.fields["FR_response_%d" % response.id] = \
        #        forms.CharField(label=_(response.question.__unicode__()),
        #                        required=True,
        #                        widget=forms.Textarea(),)
        #for response in self.instance.multiplechoiceresponse_set.all():
        #    self.fields["MC_response_%d" % response.id] = \
        #        forms.ModelChoiceField(label=_(response.question.__unicode__()),
        #                               required=True,
        #                               queryset=response.question.multiplechoiceoption_set.all(),
        #                               empty_label=None,
        #                               widget=forms.RadioSelect())
            
    def save(self):
        """
        Save the student's responses.
        """
        for response in self.instance.freeresponseresponse_set.all():
            response.response = self.cleaned_data.get("FR_response_%d" % response.id)
            response.save()
        for response in self.instance.multiplechoiceresponse_set.all():
            response.option = self.cleaned_data.get("MC_response_%d" % response.id)
            response.save()
