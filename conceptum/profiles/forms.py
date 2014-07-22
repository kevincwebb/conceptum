from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib import messages

from .models import ContributorProfile

User = get_user_model()

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = ContributorProfile
        fields = ['name', 'institution', 'homepage', 'text_info']
        
    name = forms.CharField(label=_("Name"),
                           max_length=255,
                           widget=forms.TextInput())
    
    def save(self, request):
        user = User.objects.get(pk=request.user.id)
        profile = user.profile
        data = self.cleaned_data
        
        user.name = data.get('name')
        user.save()
        
        profile.homepage = data.get('homepage')
        profile.institution = data.get('institution')
        profile.text_info = data.get('text_info')
        profile.save()
        
        messages.add_message(request, messages.INFO, 'Profile successfully updated')