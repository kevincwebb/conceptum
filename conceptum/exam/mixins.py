from django.core.exceptions import PermissionDenied

from .models import Exam


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
    Requires that an exam be a survey
    """
    def render_to_response(self, context, **response_kwargs):
        response_kwargs['current_app'] = resolve(self.request.path).namespace
        return super(SurveyMixin, self).render_to_response(context, **response_kwargs)

