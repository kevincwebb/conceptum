from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Exam, ExamKind




class DevelopmentMixin(object):
    """
    Use this mixin for views with a specific exam or question object.
    Gets the exam object (or 404 if not found) and sets the attribute self.exam.
    Raises PermissionDenied if the exam is not in the development stage (ExamKind=DEV)

    To use with a view, you must pass 'exam_id' or 'question_id' to the view as a keyword
    argument. If 'question_id' is used, you must provide second argument, 'question_type',
    either as another kwarg or by defining it as a field in the view. 'question_type' should
    be the string 'fr' or 'mc'.

    Alternatively, you can override the get_exam_for_mixin() function to return an exam
    object another way.
    """
    def get_exam_for_mixin(self):
        """
        expects url kwarg 'exam_id' or 'question_id'
        override this if you need to get the exam another way
        """
        if self.kwargs['exam_id']:
            return get_object_or_404(Exam, pk=self.kwargs['exam_id'])
        if self.kwargs[question_id]:
            if self.kwargs['question_type']:
                question_type = self.kwargs['question_type']
            elif self.question_type:
                question_type = self.question_type
            if question_type == 'fr':
                return get_object_or_404(FreeResponseQuestion, pk=question_type).exam
            if question_type == 'mc':
                return get_object_or_404(MultipleChoiceQuestion, pk=question_type).exam
        return ImproperlyConfigured('DevelopmentMixin was not provided with correct kwargs')
    
    def dispatch(self, request, *args, **kwargs):
        self.exam = self.get_exam_for_mixin()
        if not self.exam.can_develop():
            raise PermissionDenied  # Return a 403
        return super(DevelopmentMixin, self).dispatch(request, *args, **kwargs)
    
    
#class DistributeMixin(object):
#    """
#    Requires that an exam be in the distribution stage
#    """
#    def get_exam():
#        """
#        expects url kwarg 'exam_id'
#        override this to get exam another way, such as question.exam
#        """
#        get_object_or_404(Exam, pk=self.kwargs['exam_id'])
#    
#    def dispatch(self, request, *args, **kwargs):
#        self.exam = self.get_exam()
#        if not exam.stage == Exam.DIST:
#            raise PermissionDenied  # Return a 403
#        return super(DistributeMixin, self).dispatch(request, *args, **kwargs)
    
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
    def dispatch(self, request, *args, **kwargs):
        self.current_app = request.resolver_match.namespace
        if self.current_app == 'survey':
            self.exam_kind = ExamKind.SURVEY
        if self.current_app == 'CI_exam':
            self.exam_kind = ExamKind.CI
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

