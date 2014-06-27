from django import forms
from django.utils.translation import ugettext_lazy as _

from profiles.models import ContributorProfile

class SignupForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs=
                                                    {'type': 'email',
                                                     'placeholder': _('E-mail address')}))
    name = forms.CharField(label=_("Name"),
                               max_length=255,
                               widget=forms.TextInput(attrs=
                                                    {'placeholder': _('Your name'),
                                                     'autofocus': 'autofocus'}))
    
    homepage = forms.URLField(label=_("Homepage"),
                                max_length=200,
                                widget=forms.URLInput(attrs=
                                                        {'type': 'url',
                                                         'placeholder': _('Faculty homepage')}))
    




#    def __init__(self, *args, **kwargs):
#        super(SignupForm, self).__init__(*args, **kwargs)
#        field_order = ['name', 'email']

    def signup(self, request, user):
        """
        Invoked at signup time to complete the signup of the user.
        
        This method is required by allauth, but we are currently using the save_user
        methond in adapter.py to take care of things.  Should we do something here?
        """
        user_homepage = form.cleaned_data.get('homepage')
        user_profile = ContributorProfile(user=user,
                                          homepage=user_homepage,
                                          interest_in_devel=False,
                                          interest_in_deploy=False,
                                          text_info = "" )
        user_profile.save()