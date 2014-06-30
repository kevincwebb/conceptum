from django import forms

from django.utils.translation import ugettext_lazy as _
from allauth.account.forms import LoginForm as BaseLoginForm
from django.contrib.auth import authenticate

from profiles.models import ContributorProfile

class SignupForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'type': 'email',
                                                           'placeholder': _('E-mail address')}))
    name = forms.CharField(label=_("Name"),
                           max_length=255,
                           widget=forms.TextInput(attrs={'placeholder': _('Your name'),
                                                         'autofocus': 'autofocus'}))
    
    homepage = forms.URLField(label=_("Homepage"),
                              max_length=200,
                              widget=forms.URLInput(attrs={'type': 'url',
                                                           'placeholder': _('Faculty homepage')}))
    
    interest_in_devel = forms.BooleanField(label=_("I am interested in helping with CI development"),
                                           required=False,
                                           )

    interest_in_deploy = forms.BooleanField(label=_("I am interested in helping to deploy the CI"),
                                           required=False,
                                           )
    
    text_info = forms.CharField(label=_("Anything else we should know?"),
                                required=False,
                                widget=forms.Textarea())



#    def __init__(self, *args, **kwargs):
#        super(SignupForm, self).__init__(*args, **kwargs)
#        field_order = ['name', 'email']

    def signup(self, request, user):
        """
        Invoked at signup time to complete the signup of the user.
        """
        user_homepage = self.cleaned_data.get('homepage')
        user_i_devel = self.cleaned_data.get('interest_in_devel')
        user_i_deploy = self.cleaned_data.get('interest_in_deploy')
        user_text_info = self.cleaned_data.get('text_info')
        user_profile = ContributorProfile(user=user,
                                          homepage=user_homepage,
                                          interest_in_devel=user_i_devel,
                                          interest_in_deploy=user_i_deploy,
                                          text_info=user_text_info )
        user_profile.save()
        
class LoginForm(BaseLoginForm):
    
    #def clean(self):
    #    try:
    #        return super(LoginForm,self)
    #    except forms.ValidationError:
    #        if self._errors:
    #            return
    #        user = authenticate(**self.user_credentials())
    #        self.user = user
    #        return self.cleaned_data
    #    
    #
    
    def clean(self):
        if self._errors:
            return
        user = authenticate(**self.user_credentials())
        if user:
            self.user = user
        else:
            if app_settings.AUTHENTICATION_METHOD \
                    == AuthenticationMethod.EMAIL:
                error = _("The e-mail address and/or password you specified"
                          " are not correct.")
            elif app_settings.AUTHENTICATION_METHOD \
                    == AuthenticationMethod.USERNAME:
                error = _("The username and/or password you specified are"
                          " not correct.")
            else:
                error = _("The login and/or password you specified are not"
                          " correct.")
            raise forms.ValidationError(error)
        return self.cleaned_data
