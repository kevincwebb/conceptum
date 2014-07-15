from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib import messages

from allauth.account.forms import SignupForm

from .models import ContributorProfile

User = get_user_model()

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = ContributorProfile
        fields = ['name', 'institution', 'homepage', 'text_info']
        
    name = forms.CharField(label=_("Name"),
                           required=False,
                           max_length=255,
                           widget=forms.TextInput(attrs={'placeholder': _('Update your name'),
                                                         'autofocus': 'autofocus'}))
    
    institution = forms.CharField(label=_("Institution"),
                                  required=False,
                                  max_length=200,
                                  widget=forms.TextInput(attrs={'placeholder': _('Update your institution')}))
    
    homepage = forms.URLField(label=_("Homepage"),
                              required=False,
                              max_length=200,
                              widget=forms.URLInput(attrs={'type': 'url',
                                                           'placeholder': _('Update your homepage')}))
    
    text_info = forms.CharField(label=_("Other info"),
                                required=False,
                                widget=forms.Textarea())
    
    def save(self, request):
        """
        Invoked at signup time to complete the signup of the user.
        """
        user = User.objects.get(pk=request.user.id)

        
        user_name = self.cleaned_data.get('name')
        user_institution = self.cleaned_data.get('institution')
        user_homepage = self.cleaned_data.get('homepage')
        user_text_info = self.cleaned_data.get('text_info')
        
        if user_name:
            user.name = user_name
            messages.add_message(request, messages.INFO, 'Name successfully updated.')
            user.save()
        if user_homepage:
            user.profile.homepage = user_homepage
            messages.add_message(request, messages.INFO, 'Homepage successfully updated.')
        if user_institution:
            user.profile.institution = user_institution
            messages.add_message(request, messages.INFO, 'Institution successfully updated.')
        if user_text_info:
            user.profile.text_info = user_text_info
            messages.add_message(request, messages.INFO, 'Info successfully updated.')
        user.profile.save()
