from django import forms
#from django.contrib.auth import get_user_model

#User = get_user_model()

class DistributeForm(forms.Form):
    
    class Meta:
        fields = ['email']
        
    email = forms.EmailField(widget=forms.TextInput(attrs={'type': 'email'}))