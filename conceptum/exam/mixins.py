from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import resolve

from .models import Exam, ExamKind




class DevelopmentMixin(object):
    """
    Requires that an exam be in the development stage
    """
    def get_exam_for_mixin():
        """
        expects url kwarg 'exam_id"
        override this to get the exam object another way, such as question.exam
        """
        return get_object_or_404(Exam, pk=self.kwargs['exam_id'])
    
    def dispatch(self, request, *args, **kwargs):
        self.exam = self.get_exam()
        if not exam.can_develop():
            raise PermissionDenied  # Return a 403
        return super(DevelopmentMixin, self).dispatch(request, *args, **kwargs)
    
    
class DistributeMixin(object):
    """
    Requires that an exam be in the distribution stage
    """
    def get_exam():
        """
        expects url kwarg 'exam_id"
        override this to get exam another way, such as question.exam
        """
        get_object_or_404(Exam, pk=self.kwargs['exam_id'])
    
    def dispatch(self, request, *args, **kwargs):
        self.exam = self.get_exam()
        if not exam.stage == Exam.DIST:
            raise PermissionDenied  # Return a 403
        return super(DistributeMixin, self).dispatch(request, *args, **kwargs)
    
class ExamKindMixin(object):
    """
    Many views need to distinguish between kinds of exams. For example, a view that lists
    exam objects should list only surveys or only CI exams, depending on what stage we
    are at.
    
    This mixin saves the appropriate ExamKind to self.kind
    """
    def dispatch(self, request, *args, **kwargs):
        r = resolve(request.path)
        if r.namespace == 'survey':
            self.kind = ExamKind.SURVEY
        if r.namespace == 'CI_exam':
            self.kind = ExamKind.CI
        return super(ExamKindMixin, self).dispatch(request, *args, **kwargs)

    #def render_to_response(self, context, **response_kwargs):
    #    response_kwargs['current_app'] = resolve(self.request.path).namespace
    #    return super(ExamKindMixin, self).render_to_response(context, **response_kwargs)

