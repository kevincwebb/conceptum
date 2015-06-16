from datetime import timedelta

from django.db import models
from django.contrib.contenttypes.models import ContentType, ContentTypeManager
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.utils import timezone
from django.core.urlresolvers import reverse

from allauth.account.adapter import get_adapter
import reversion
from reversion.models import Revision, Version

from profiles.models import ContributorProfile
from .managers import ExamResponseManager

# Constants
EXAM_NAME_LENGTH = 100
EXAM_DESC_LENGTH = 500
QUESTION_LENGTH = 1000
CHOICE_LENGTH = 500
RESPONSE_FREE_LENGTH = 2000
RESPONDENT_NAME_LENGTH = 100
COURSE_NAME_LENGTH = 100

"""
IMPORTANT NOTE: This app has a dependency on allauth for some of the behind-the-scences
email generation in ExamResponse.send()
"""

class Exam(models.Model):
    """
    Represents a collection of questions that can be used as a concept
    inventory, survey, or other form of exam.
    """
    name = models.CharField(max_length=EXAM_NAME_LENGTH)
    description = models.CharField(max_length=EXAM_DESC_LENGTH)
    randomize = models.BooleanField('randomize question order', default=False)        
    
    def __unicode__(self):
        return self.name
#reversion.register(Exam)


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
    
#class OptionVersion(models.Model):
#    revision = models.ForeignKey(Revision)  # This is required
#    question= models.ForeignKey(Version)
    
reversion.register(MultipleChoiceOption)
reversion.register(MultipleChoiceQuestion, follow=["multiplechoiceoption_set"])


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
    
    #objects = QuestionResponseManager()
    
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
