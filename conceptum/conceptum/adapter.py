from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import get_user_model

class AccountAdapter(DefaultAccountAdapter):
    
     def new_user(self, request):
        """
        Instantiates a new User instance.
        """
        user = get_user_model()()
        user.is_active = False
        return user
    