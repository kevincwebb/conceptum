
from django import forms

class SignupForm(forms.Form):
    name = forms.CharField(label=("Name"),
                               max_length=255,
                               widget=forms.TextInput(
                                   attrs={'placeholder':
                                          ('Full name'),
                                          'autofocus': 'autofocus'}))
    
    def signup(self, request, user):
        """
        Invoked at signup time to complete the signup of the user.
        """
        pass