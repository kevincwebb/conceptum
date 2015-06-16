from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib import messages

from .models import ContributorProfile

User = get_user_model()

class EditProfileForm(forms.ModelForm):
    """
    Form for users to edit their user/profile information.
    Name, Institution, Homepage, and Text info are editable fields.
    """
    class Meta:
        model = ContributorProfile
        fields = ['name', 'institution', 'homepage', 'text_info']
        
    name = forms.CharField(label=_("Name"),
                           max_length=255,
                           widget=forms.TextInput())
    
    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def save(self, request):
        """
        Save the updated information to the database.
        """
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
