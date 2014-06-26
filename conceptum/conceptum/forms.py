from django import forms
from django.utils.translation import pgettext, ugettext_lazy as _, ugettext

class SignupForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs=
                                                    {'type': 'email',
                                                     'placeholder':
                                                     _('E-mail address')}))
    name = forms.CharField(label=_("Name"),
                               max_length=255,
                               widget=forms.TextInput(
                                   attrs={'placeholder':
                                          _('Your name'),
                                          'autofocus': 'autofocus'}))
    
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        field_order = ['name', 'email']

    def signup(self, request, user):
        """
        Invoked at signup time to complete the signup of the user.
        """
        pass