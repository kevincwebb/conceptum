from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Exam, ExamKind


class DevelopmentMixin(object):
    """
    If you use this mixin in a view you must also use CurrentAppMixin.
    Use this mixin for views with a specific exam or question object.
    Gets the exam object (or 404 if not found).
    Sets the attribute `self.exam` so it can be used in the view.
    Raises PermissionDenied if the exam's kind does not match the current app.
    Raises PermissionDenied if the exam is not in the development stage (ExamKind=DEV).

    You must pass 'exam_id' or 'question_id' to your view as a keyword argument.
    If 'question_id' is used, this mixin checks self.model to determine if the
    question is a FreeResponseQuestion or MultipleChoiceQuestion. You can alternatively
    override the get_exam_for_mixin() function to return an exam object another way.
    """
    def get_exam_for_mixin(self):
        """
        expects url kwarg 'exam_id' or 'question_id'
        override this if you need to get the exam another way
        """
        if self.kwargs.get('exam_id'):
            return get_object_or_404(Exam, pk=self.kwargs['exam_id'])
        if self.kwargs.get('question_id'):
            if self.model:
                return get_object_or_404(self.model, pk=self.kwargs['question_id']).exam
        return ImproperlyConfigured('DevelopmentMixin was not provided with correct kwargs')
    
    def dispatch(self, request, *args, **kwargs):
        """
        note: calls CurrentAppMixin's set_current_app method
        """
        assert issubclass(self.__class__, CurrentAppMixin)
        self.exam = self.get_exam_for_mixin()
        self.set_current_app(request)
        if (self.exam.kind != self.exam_kind
            or not self.exam.can_develop()):
                raise PermissionDenied
        return super(DevelopmentMixin, self).dispatch(request, *args, **kwargs)
    
    
class DistributionMixin(object):
    """
    If you use this mixin in a view you must also use CurrentAppMixin.
    Use this mixin for views with a specific exam.
    Gets the exam object (or 404 if not found).
    Sets the attribute `self.exam` so it can be used in the view.
    Raises PermissionDenied if the exam's kind does not match the current app.
    Raises PermissionDenied if the exam is not in the distribution stage (ExamKind=DIST).

    To use with a view, you must pass 'exam_id' to the view as a keyword argument,
    or override the get_exam_for_mixin() function to return an exam object another way.
    """
    def get_exam_for_mixin(self):
        """
        expects url kwarg 'exam_id'
        override this if you need to get the exam another way
        """
        if self.kwargs.get('exam_id'):
            return get_object_or_404(Exam, pk=self.kwargs['exam_id'])
        return ImproperlyConfigured('DistributeMixin was not provided with correct kwargs')
    
    def dispatch(self, request, *args, **kwargs):
        """
        note: calls CurrentAppMixin's set_current_app method
        """
        assert issubclass(self.__class__, CurrentAppMixin)
        self.exam = self.get_exam_for_mixin()
        self.set_current_app(request)
        if (self.exam.kind != self.exam_kind
            or not self.exam.can_distribute()):
                raise PermissionDenied
        return super(DistributionMixin, self).dispatch(request, *args, **kwargs)


class CurrentAppMixin(object):
    """
    Gets information from the url namespace in order to determine the current app.
    This info can be used in views to filter exam objects by kind (survey or CI),
    and to stay within the same app when reversing url names.
    
    sets the following attributes on the view object:
        current_app - 'survey' or 'CI_exam'
        exam_kind - ExamKind.SURVEY or ExamKind.CI_exam
    
    To filter objects by kind:
        - Exam.objects.filter(kind=self.exam_kind)
    
    To get a url for the current app:
        - reverse('exam:index', current_app=self.current_app)   
        - {% url exam:index %} {# current_app is automatically placed in response #}
            
    {{ current_app }} is also available as a template variable
    """
    def set_current_app(self, request):
        """
        note that this function is expected by DevelopmentMixin and DistributionMixin
        """
        self.current_app = request.resolver_match.namespace
        if self.current_app == 'survey':
            self.exam_kind = ExamKind.SURVEY
        if self.current_app == 'CI_exam':
            self.exam_kind = ExamKind.CI
    
    def dispatch(self, request, *args, **kwargs):
        self.set_current_app(request)
        return super(CurrentAppMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self,**kwargs):
        context = super(CurrentAppMixin, self).get_context_data(**kwargs)
        if self.current_app == 'survey':
            context['current_app'] = 'survey'
        if self.current_app == 'CI_exam':
            context['current_app'] = 'CI'
        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Provides current_app to template context so that, e.g.,
            
            {% url exam:index %}
            
        automatically redirects to the index page for the current app (survey or CI_exam)
        """
        response_kwargs['current_app'] = self.current_app
        return super(CurrentAppMixin, self).render_to_response(context, **response_kwargs)