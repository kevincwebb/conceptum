from authtools.models import User as BaseUser
from simple_email_confirmation import SimpleEmailConfirmationUserMixin
 
    
class User(SimpleEmailConfirmationUserMixin, BaseUser):
    class Meta:
        proxy = True