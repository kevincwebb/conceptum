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


class ResponseSet(models.Model):
    """
    This class holds information shared among multiple ExamResponses that have
    been distributed together (same course, teacher, time)
    
    pre_test = True implies the test was given as a pre_test, and a post_test should follow
    pre_test = False implies the test was given as a post_test
    
    "modules" field is currently unused because stage1 is not ready yet.
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
    Class for distributing and saving a single instance of an Exam.
    Use self.freeresponseresponse_set (or multiplechoiceresponse_set) to get a queryset
    of FreeResponseResponses (MultipleChoiceResponses) associated with this ExamResponse.
    
    Because this object is not associated with a single Exam, it is possible to
    use multiple Exam objects when distributing exam_responses
    
    Use objects.create() when creating in order to set the key
    
    Email functionality based on django-allauth,
    see allauth.account.models.EmailConfirmation
    and allauth.account.adapter.send_mail
    
    TODO: Set up an automatic deletion of expired blank responses.
    this S.O. post is a good design http://stackoverflow.com/a/11789141
    """
    
    key = models.CharField(max_length=64, unique=True, primary_key=True)
    response_set = models.ForeignKey(ResponseSet)
    respondent = models.CharField(max_length=RESPONDENT_NAME_LENGTH, default='') # an email
    expiration_datetime = models.DateTimeField()
    sent = models.DateTimeField(null=True)
    submitted = models.DateTimeField(null=True, blank=True, default=None)
    
    objects = ExamResponseManager()
    
    def is_available(self):
        return (not self.submitted) and self.expiration_datetime >= timezone.now()
    
    def send(self, request, email, **kwargs):
        """
        Generates an email message with a link to the ExamResponse form.
        
        This function calls get_adapter() from django-allauth and uses allauth's
        send_mail function.
        """
        current_site = Site.objects.get_current()
        test_url = reverse("exam_response", args=[self.key])
        test_url = request.build_absolute_uri(test_url)
        # The ctx dictionary is a way to access variables in the message template,
        # no need to get into the send_mail function below.
        ctx = {
            "test_url": test_url,
            "current_site": current_site,
            "key": self.key,
            "expiration": self.expiration_datetime
        }
        email_template = 'exam/email_test' # "_message.txt" or "_subject.txt" will be added
        # get_adapter and send_mail depend on django-allauth
        get_adapter().send_mail(email_template,
                                email,
                                ctx)
        self.sent = timezone.now()
        self.save()

    def __unicode__(self):
        return "{0}: {1}".format(self.key[-8:], self.respondent)

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

class QuestionResponse(models.Model):
    """
    Base class for *Response models.  Subclasses should define a
    "question" field that is a ForeignKey to a *Question model.
    
    This model is abstract. Using multi-inheritence would be less efficient than an
    abstract model, but would allow us to query all questionresponse objects.
    """
    exam_response = models.ForeignKey(ExamResponse)
    
    #objects = QuestionResponseManager()
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return "{0}: {1}".format(self.exam_response, self.question)


class FreeResponseQuestion(Question):
    """
    Represents a question in which the answerer can respond with free-form
    text.
    """
    pass

class FreeResponseResponse(QuestionResponse):
    """
    Records the response to a free response question.
    """
    question = models.ForeignKey(FreeResponseQuestion)
    response = models.CharField(max_length=RESPONSE_FREE_LENGTH, blank=True)


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



class MultipleChoiceResponse(QuestionResponse):
    """
    Records the response to a multiple choice question.
    """
    question = models.ForeignKey(MultipleChoiceQuestion)
    option = models.ForeignKey(MultipleChoiceOption, null=True)
