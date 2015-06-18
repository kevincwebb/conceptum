from datetime import timedelta

from django.db import models, IntegrityError
from django.contrib.contenttypes.models import ContentType, ContentTypeManager
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone


from allauth.account.adapter import get_adapter
from django_enumfield import enum
#import reversion
#from reversion.models import Revision, Version

from profiles.models import ContributorProfile
from .managers import ExamResponseManager

# Constants
EXAM_NAME_LENGTH = 100
EXAM_DESC_LENGTH = 500
QUESTION_LENGTH = 1000
CHOICE_LENGTH = 500
MAX_CHOICES = 6
REQUIRED_CHOICES = 1
RESPONSE_FREE_LENGTH = 2000
RESPONDENT_NAME_LENGTH = 100
COURSE_NAME_LENGTH = 100


"""
IMPORTANT NOTE: This app has a dependency on allauth for some of the
behind-the-scences email generation in ExamResponse.send()
"""

class ExamKind(enum.Enum):
    """
    an Enum-class (see django-enumfield) with 2 values:
        SURVEY - The exam is a survey; it will be used to collect preliminary
                    data on student thinking.
        CI     - The exam is a Concept Inventory; it is the exam that will be
                    used to collect final data.
    
    While a boolean field could have been used, this leaves the possibility of
    having a type of exam that is neither a survey nor a CI. This would be done
    by adding a field to this class.
    """
    SURVEY = 0
    CI = 1

    labels = {
        SURVEY: 'Survey',
        CI: 'CI'
    }
    
    # This would enforce that an exam cannot change kind
    # _transitions = {}


class ExamStage(enum.Enum):
    """
    an Enum-class (see django-enumfield) with 3 values:
        DEV   - The exam is in development stage.
        DIST  - The exam is in distribution stage. It cannot be edited.
        CLOSE - The exam is closed. Its data will be available, but it cannot
                    be edited or distributed.
    
    acceptable state transitions:
        DEV --> DIST
        DEV --> CLOSED
        DIST--> CLOSED
        
    Attempting to change the value from e.g. CLOSED to DEV throws an
    InvalidStatusOperationError.
    
    Once an exam leaves the development stage, it needs to be locked against further changes
    because it may have begun to be distributed.
    """
    CLOSED = 0
    DEV = 1
    DIST = 2
    
    labels = {
        CLOSED: 'Closed',
        DEV: 'Development',
        DIST: 'Distribution',
    }
    
    _transitions = {
        CLOSED: (DEV, DIST),
        DIST: (DEV,)
    }


class Exam(models.Model):
    """
    Represents a collection of questions that can be used as a concept
    inventory, survey, or other form of exam.
    
    The kind of exam is recorded in the 'kind' field. This is an EnumField with
    2 options: SURVEY and CI. Surveys and CIs have different uses in the overall
    project, so this field allows us to distinguish between them.
    
    The stage of the exam (another EnumField) refers to the exam's own stage.
    It is available for development, distribution, or neither (closed). Views,
    forms, etc. should check the stage before performing operations on exam
    objects. All Questions will raise 
    """
    name = models.CharField(max_length=EXAM_NAME_LENGTH)
    description = models.CharField(max_length=EXAM_DESC_LENGTH)
    randomize = models.BooleanField('randomize question order', default=False)        
    
    kind = enum.EnumField(ExamKind, default=ExamKind.CI)
    stage = enum.EnumField(ExamStage, default=ExamStage.DEV)
    
    def __unicode__(self):
        return self.name

    def can_develop(self):
        return self.stage == ExamStage.DEV
    
    def can_distribute(self):
        return self.stage == ExamStage.DIST
    
    def is_survey(self):
        return self.kind == ExamKind.SURVEY
    
    def is_CI(self):
        return self.kind == ExamKind.CI

def question_imageupload_to(question, filename):
    """
    Determines the path to use, within the media root, when storing an uploaded
    image file for an exam question.

    Args:
        question: An instance of the question model for which the image is
            being uploaded.
        filename: The name of the file being uploaded.
    """
    return 'exams/%d/%s' % (question.exam.pk, filename)


class Question(models.Model):
    """
    Abstract base class that represents one question within an exam.
    """
    exam = models.ForeignKey(Exam)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    
    question = models.CharField(max_length=QUESTION_LENGTH)
    image = models.ImageField(upload_to=question_imageupload_to, blank=True)
    rank = models.IntegerField(null=True, blank = True)
    optional = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.question
    
    def clean(self):
        """
        Validate that forms are not trying to modify exams unless they are
        in the development stage.
        """
        if not exam.can_develop():
            raise ValidationError('This exam is no longer editable')
        super(Question, self).save(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        """
        Questions should not be editable unless exam.can_develop()
        """
        if not exam.can_develop():
            raise IntegrityError('This exam is no longer editable')
        super(Question, self).save(*args, **kwargs)


class FreeResponseQuestion(Question):
    """
    Represents a question in which the answerer can respond with free-form
    text.
    """
    pass


class MultipleChoiceQuestion(Question):
    """
    Represents a question in which the answerer must choose between a set of
    predefined choices.
    """
    randomize = models.BooleanField('randomize choices order', default=False)


class MultipleChoiceOption(models.Model):
    """
    Represents one option in the set of choices for a multiple choice question.
    """
    question = models.ForeignKey(MultipleChoiceQuestion)
    text = models.CharField(max_length=CHOICE_LENGTH)
    rank = models.IntegerField(null=True, blank = True)

    def __unicode__(self):
        return self.text

    def clean(self):
        """
        Validate that forms are not trying to modify exams unless they are
        in the development stage.
        """
        if not question.exam.can_develop():
            raise ValidationError('This exam is no longer editable')
        super(MultipleChoiceOption, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        """
        Options should not be editable unless exam.can_develop()
        """
        if not question.exam.can_develop():
            raise IntegrityError('This exam is no longer editable')
        super(MultipleChoiceOption, self).save(*args, **kwargs)
    

class ResponseSet(models.Model):
    """
    When an instructor distributes an exam, the individual exams (ExamResponse) are
    all connected to one ResponseSet that holds information for that distribution.
    
    First, a ResponseSet is created with course and instructor information and modules
    are selected.  Then, emails are supplied and an ExamResponse is created for each
    email address.  Each ExamRespons has a ForeignKey relationship with the ResponseSet.
    
    pre_test = True  implies the test was given as a pre_test, and a post_test should follow
    pre_test = False implies the test was given as a post-test (there may not have been a pre-test)
    
    "modules" field is currently unused because stage1 is not ready yet.
    
    TODO: incorporate modules
    """
    created = models.DateTimeField(auto_now_add=True)
    instructor = models.ForeignKey(ContributorProfile) # includes name, email, and institution
    course = models.CharField(max_length=COURSE_NAME_LENGTH)
    pre_test = models.BooleanField(default=False)
    exam = models.ForeignKey(Exam)
    # modules = models.ManyToManyField(...
    
    class Meta:
        ordering = ['-created']
    
    def __unicode__(self):
        return "{0} ({1})".format(self.course, self.created.date())
    
    
class ExamResponse(models.Model):
    """
    A model for distributing and saving a student's responses to an exam.  Specific
    responses to questions are stored in QuestionResponses.
    
    Fields:
        key: Every ExamResponse has a unique 64-digit key. Use objects.create() to
            create a new ExamResponse with an automatically generated key. This field
            is the primary_key for this model.
            
        response_set: ForeignKey to the ResponseSet this ER is associated with.
        
        respondent: Email address the ER was sent to.
        
        expiration_datetime: If the ER has expired, it should not be available for a
            student to access.  Expired, unsubmitted responses can be deleted by a staff
            user.
        
        sent: This field is set in the send() method.
        
        submitted: Date submitted.  Defaults to None, which means that this ER has not
            been submitted yet.  If submitted is not None, it should not be available.
    
    To get a queryset of QuestionResponses associated with an ExamResponse, use
    self.freeresponseresponse_set or multiplechoiceresponse_set
    
    
    Email functionality based on django-allauth, for original design see
        allauth.account.models.EmailConfirmation
        allauth.account.adapter.send_mai
    """
    
    key = models.CharField(max_length=64, unique=True, primary_key=True)
    response_set = models.ForeignKey(ResponseSet)
    respondent = models.CharField(max_length=RESPONDENT_NAME_LENGTH, default='') # an email
    expiration_datetime = models.DateTimeField()
    sent = models.DateTimeField(null=True)
    submitted = models.DateTimeField(null=True, blank=True, default=None)
    
    # provides a new create() method that generates a key
    objects = ExamResponseManager()
    
    def is_available(self):
        """
        An ExamResponse is available if it has not been submitted and it has not
        expired.
        """
        return (not self.submitted) and self.expiration_datetime >= timezone.now()
    
    def send(self, request, email, **kwargs):
        """
        Generates an email message with a link to the ExamResponse form.  The link
        is generated using self.key.
        
        This function calls get_adapter() from django-allauth and uses allauth's
        send_mail function.
        """
        current_site = Site.objects.get_current()
        test_url = reverse("exam_response", args=[self.key])
        test_url = request.build_absolute_uri(test_url)
        # The ctx dictionary is a way to create variables to be used in the message
        # template (no need to get into the send_mail function below.)
        ctx = {
            "test_url": test_url,
            "current_site": current_site,
            "key": self.key,
            "expiration": self.expiration_datetime
        }
        # email_template is a prefix, '_message.txt' or '_subject.txt' will be added
        email_template = 'exam/email_test'
        # get_adapter and send_mail depend on django-allauth
        get_adapter().send_mail(email_template,
                                email,
                                ctx)
        self.sent = timezone.now()
        self.save()

    def __unicode__(self):
        # "00000000: email@email.com"
        return "{0}: {1}".format(self.key[-8:], self.respondent)


class QuestionResponse(models.Model):
    """
    Base class for *Response models.  Subclasses should define a
    "question" field that is a ForeignKey to a *Question model.
    
    This model is abstract.
    """
    exam_response = models.ForeignKey(ExamResponse)
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return "{0}: {1}".format(self.exam_response, self.question)


class FreeResponseResponse(QuestionResponse):
    """
    Records the response to a free response question.
    """
    question = models.ForeignKey(FreeResponseQuestion)
    response = models.CharField(max_length=RESPONSE_FREE_LENGTH, blank=True)


class MultipleChoiceResponse(QuestionResponse):
    """
    Records the response to a multiple choice question.
    """
    question = models.ForeignKey(MultipleChoiceQuestion)
    option = models.ForeignKey(MultipleChoiceOption, null=True)
