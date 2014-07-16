import logging

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from braces.views import LoginRequiredMixin, UserPassesTestMixin

from .models import Interview
from .forms import AddForm, EditForm

logger = logging.getLogger(__name__)

# TODO: check permissions to allow users into certain pages

class IndexView(LoginRequiredMixin, generic.ListView):
	template_name = 'interviews/index.html'
	context_object_name = 'interview_list'
	
	def get_queryset(self):
		return Interview.objects.all()


class DetailView(LoginRequiredMixin, generic.DetailView):
	model=Interview
	template_name = 'interviews/detail.html'


class AddView(LoginRequiredMixin, generic.CreateView):
    model = Interview
    template_name = 'interviews/add.html'
    form_class = AddForm

    def form_valid(self, form):
        self.object = form.save(self.request)
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return self.object.get_absolute_url()
    

class EditView(LoginRequiredMixin,
               UserPassesTestMixin,
               generic.UpdateView):
    model = Interview
    template_name = 'interviews/edit.html'
    form_class = EditForm
    
    # Raise a 403 if user is denied access
    raise_exception = True
    
    # Expected by UserPassesTestMixin
    def test_func(self, user):
        interview_id = self.kwargs['pk']
        interview = get_object_or_404(self.model, pk=interview_id)
        return (user.is_staff or user==interview.uploaded_by)
    
    def dispatch(self, *args, **kwargs):
        #interview_id = self.kwargs['pk']
        #user = self.get_object_or_404(self.model,pk=interview_id)
        #if not (self.request.user.is_staff or self.request.user==self.object.uploaded_by):
        #    raise PermissionDenied
        return super(EditView, self).dispatch(*args, **kwargs)
        
    
    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return self.object.get_absolute_url()

    
class DeleveView(LoginRequiredMixin, generic.DeleteView):
    pass
