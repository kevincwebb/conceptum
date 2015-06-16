from django.core.exceptions import PermissionDenied

class ContribRequiredMixin(object):
    """
    View mixin which verifies that the logged in user is allowed to contribute
    (user.profile.is_contrib==True or user.is_staff==True).
    
    Works similar to django-braces mixins, but always raises a PermissionDenied
    if the user fails the test, unlike the django-braces mixins which have
    class settings to determine the behavior.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Check to see if the user in the request is allowed to contribute.
        Uses the can_contrib() method just in case there are inconsistencies
        between is_staff and is_contrib booleans.
        """
        if not request.user.profile.can_contrib():
            raise PermissionDenied  # Return a 403
        return super(ContribRequiredMixin, self).dispatch(request, *args, **kwargs)