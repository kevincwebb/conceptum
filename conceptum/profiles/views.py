from django.views.generic.base import TemplateView
from django.shortcuts import redirect


class ProfileView(TemplateView):
    template_name = 'profiles/profile.html'
    redirect_field_name = "account_login"
    
    def get_redirect_url(self):
        return self.redirect_field_name
    
    def get(self, request, *args, **kwargs):
        '''
        Overriding TemplateView.get() in order to
        prevent active user from seeing inactive page
        '''
        # Redirect to login if user is not logged in
        if not self.request.user.is_authenticated():
            return redirect(self.get_redirect_url())
        # Process normally if User is logged in yet
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
