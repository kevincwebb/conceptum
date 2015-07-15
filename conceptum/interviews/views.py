from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy, reverse
from django.views import generic
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from braces.views import LoginRequiredMixin, UserPassesTestMixin, StaffuserRequiredMixin

from profiles.mixins import ContribRequiredMixin
from .models import Interview, InterviewGroup
from .forms import AddForm, EditForm


class IndexView(LoginRequiredMixin,
                ContribRequiredMixin,
                generic.ListView):
    model = InterviewGroup
    template_name = 'interviews/index.html'


class CreateGroupView(LoginRequiredMixin,
                      StaffuserRequiredMixin,
                      generic.CreateView):
    model = InterviewGroup
    template_name = 'interviews/create.html'
    
    def get_success_url(self):
        return reverse('interview_group', args=[self.object.id])


class GroupView(LoginRequiredMixin,
                ContribRequiredMixin,
                generic.DetailView):
    """
    Lists all interviews in the database, click on an interview to go to its DetailView
    """
    template_name = 'interviews/group.html'
    model = InterviewGroup
    pk_url_kwarg = 'group_id'
    
    def get_context_data(self, **kwargs):
        """
        The hyperlink to the edit page should only be visible if this user is allowed
        to edit, i.e., this user is the original uploader or has staff privileges.
        The template should use the boolean user_can_edit to do this check
        """
        context = super(GroupView, self).get_context_data(**kwargs)
        interview_list = []
        for intv in self.object.interview_set.all():
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


class RenameView(LoginRequiredMixin,
                 StaffuserRequiredMixin,
                 generic.UpdateView):
    template_name = 'interviews/edit.html'
    model = InterviewGroup
    pk_url_kwarg = 'group_id'
    fields = ['name']
    
    def get_success_url(self):
        return reverse('interview_group', args=[self.object.id])


def lock_group(request, group_id):
    group = get_object_or_404(InterviewGroup, pk=group_id)
    group.unlocked = False
    group.save()
    return HttpResponseRedirect(reverse('interview_group', args=[group.id]))


def unlock_group(request, group_id):
    group = get_object_or_404(InterviewGroup, pk=group_id)
    group.unlocked = True
    group.save()
    return HttpResponseRedirect(reverse('interview_group', args=[group.id]))


class DetailView(LoginRequiredMixin,
                 ContribRequiredMixin,
                 generic.DetailView):
    """
    Displays all data for an interview.
    """
    model=Interview
    template_name = 'interviews/detail.html'

    def user_can_edit(self):
        return (self.object.group.unlocked and
            (self.request.user.is_staff or self.request.user==self.object.uploaded_by))
    

    def get_context_data(self, **kwargs):
        """
        The hyperlink to the edit page should only be visible if this user is allowed
        to edit, i.e., this user is the original uploader or has staff privileges.
        The template should use the boolean user_can_edit to do this check
        """
        context = super(DetailView, self).get_context_data(**kwargs)
        context['user_can_edit'] = self.user_can_edit()
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

    def dispatch(self, request, *args, **kwargs):
        group_id = self.kwargs['group_id']
        if int(group_id) == 0:
            self.group = None
        else:
            self.group = get_object_or_404(InterviewGroup, pk=group_id)        
            if not self.group.unlocked:
                raise PermissionDenied
        return super(AddView, self).dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super(AddView, self).get_form_kwargs()
        kwargs['group'] = self.group
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(AddView, self).get_context_data(**kwargs)
        context['group'] = self.group
        return context

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
    
    def dispatch(self, request, *args, **kwargs):
        interview = get_object_or_404(Interview, pk=self.kwargs['pk'])        
        if not interview.group.unlocked:
            raise PermissionDenied
        return super(EditView, self).dispatch(request, *args, **kwargs)
    
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

