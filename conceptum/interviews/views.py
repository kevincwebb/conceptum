from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from braces.views import LoginRequiredMixin, UserPassesTestMixin

from profiles.mixins import ContribRequiredMixin
from .models import Interview
from .forms import AddForm, EditForm


# TODO: check permissions to allow users into certain pages

class IndexView(LoginRequiredMixin,
                ContribRequiredMixin,
                generic.ListView):
    """
    Lists all interviews in the database, click on an interview to go to its DetailView
    """
    template_name = 'interviews/index.html'
    interview_list = []
    # for intv in Interview.objects.all():
    #     excerpts = intv.excerpt_set.all()
    #     interview = [intv]
    #     interview.extend(excerpts)
    #     interview_list.append(interview)
    
    context_object_name = 'interview_list'
    
    
    def get_context_data(self, **kwargs):
        """
        The hyperlink to the edit page should only be visible if this user is allowed
        to edit, i.e., this user is the original uploader or has staff privileges.
        The template should use the boolean user_can_edit to do this check
        """
        
        context = super(IndexView, self).get_context_data(**kwargs)
        interview_list = []
        for intv in Interview.objects.all():
            excerpts_obj = intv.excerpt_set.all()
            excerpts = []
            for exc in excerpts_obj:
                excerpts.append(exc.content_object.name)
                
            excerpts = ", ".join(excerpts)
            excerpts = "Concepts: " + excerpts
            interview = [intv]
            interview.append([excerpts, "Questions: " + len(excerpts_obj).__str__()])
            interview_list.append(interview)
        context['interview_list'] = interview_list
        return context

    def get_queryset(self):
        return Interview.objects.all()


class DetailView(LoginRequiredMixin,
                 ContribRequiredMixin,
                 generic.DetailView):
    """
    Displays all data for an interview.
    """
    model=Interview
    template_name = 'interviews/detail.html'

    def get_context_data(self, **kwargs):
        """
        The hyperlink to the edit page should only be visible if this user is allowed
        to edit, i.e., this user is the original uploader or has staff privileges.
        The template should use the boolean user_can_edit to do this check
        """
        context = super(DetailView, self).get_context_data(**kwargs)
        context['user_can_edit'] = self.request.user.is_staff or self.request.user==self.object.uploaded_by
        return context


class AddView(LoginRequiredMixin,
              ContribRequiredMixin,
              generic.CreateView):
    """
    FormView for a user to add an interview.
    """
    model = Interview
    template_name = 'interviews/add.html'
    form_class = AddForm

    def form_valid(self, form):
        """
        Calls the AddForm save method, which takes the request as an argument
        """
        self.object = form.save(self.request)
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        """
        Returns the result of the get_absolute_url method in the Interview model.
        This redirects to the interview's detail page
        """    
        return self.object.get_absolute_url()
    

class EditView(LoginRequiredMixin,
               ContribRequiredMixin,
               UserPassesTestMixin,
               generic.UpdateView):
    """
    FormView for a user to edit an existing interview.  Only the original uploader or
    a staff user is allowed to edit an interview.
    """
    model = Interview
    template_name = 'interviews/edit.html'
    form_class = EditForm
    
    raise_exception = True
    redirect_unauthenticated_users = True
    
    def test_func(self, user):
        """
        This function is required by the UserPassesTestMixin.
        Requires that the user is staff or the original uploader
        """
        interview_id = self.kwargs['pk']
        interview = get_object_or_404(self.model, pk=interview_id)
        return (user.is_staff or user==interview.uploaded_by)
    
    def get_initial(self):
        initial = {}
        for excerpt in self.object.excerpt_set.all():
            initial['response_%d' % excerpt.object_id] = excerpt.response
        return initial
    
    def form_valid(self, form):
        """
        Calls the EditForm save method
        """
        form.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        """
        Returns the result of the get_absolute_url method in the Interview model.
        This redirects to the interview's detail page
        """
        return self.object.get_absolute_url()

    
class DeleteView(LoginRequiredMixin,
                 ContribRequiredMixin,
                 UserPassesTestMixin,
                 generic.DeleteView):
       
    model = Interview
    template_name = 'interviews/confirm_delete.html'
    success_url = reverse_lazy('interview_index')
    
    raise_exception = True
    redirect_unauthenticated_users = True
    
    def test_func(self, user):
        """
        This function is required by the UserPassesTestMixin.
        Requires that the user is staff or the original uploader
        """
        interview_id = self.kwargs['pk']
        interview = get_object_or_404(self.model, pk=interview_id)
        return (user.is_staff or user==interview.uploaded_by)

