from allauth.account.adapter import DefaultAccountAdapter


from profiles.models import ContributorProfile


class AccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        super(AccountAdapter, self).save_user(request, user, form, commit=False)
        name = form.cleaned_data.get('name')
        setattr(user, 'name', name)
        user.is_active = False
        user.save()
        
        #user_homepage = form.cleaned_data.get('homepage')
        #user_profile = ContributorProfile(user=user,
        #                                  homepage=user_homepage,
        #                                  interest_in_devel=False,
        #                                  interest_in_deploy=False,
        #                                  text_info = "" )
        #user_profile.save()
        return user