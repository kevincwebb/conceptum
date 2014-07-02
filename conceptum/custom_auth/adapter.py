from allauth.account.adapter import DefaultAccountAdapter

from profiles.models import ContributorProfile


class AccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        super(AccountAdapter, self).save_user(request, user, form, commit=False)
        name = form.cleaned_data.get('name')
        setattr(user, 'name', name)
        user.is_active = False
        user.save()
        return user