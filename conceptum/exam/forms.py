from datetime import timedelta, datetime, date, time

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.validators import validate_email, ValidationError

from .models import ExamResponse, MultipleChoiceOption, ResponseSet

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
