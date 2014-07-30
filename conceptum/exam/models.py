from django.db import models
from django.contrib.contenttypes.models import ContentType, ContentTypeManager
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.utils import timezone
from django.core.urlresolvers import reverse

from allauth.account.adapter import get_adapter
# import reversion

from .managers import ExamResponseManager


# Constants
EXAM_NAME_LENGTH = 100
EXAM_DESC_LENGTH = 500
QUESTION_LENGTH = 1000
CHOICE_LENGTH = 500
RESPONSE_FREE_LENGTH = 2000
RESPONDENT_NAME_LENGTH = 100


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


class ExamResponse(models.Model):
    """
    Object for distributing and saving a single instance of an Exam.
    Use self.question_response_set to get a queryset of QuestionResponses
    associated with this ExamResponse.
    
    Because this object is not associated with a single Exam, it is possible to
    use multiple Exams when distributing exams (thus allowing modular exams)
    
    Use objects.create() when creating in order to set the key
    
    email functionality based on allauth
    see allauth/account/model.py - EmailConfirmation
    """
    # We may want to make the respondent field anonymous or optional
    respondent = models.CharField(max_length=RESPONDENT_NAME_LENGTH, default='')
    is_available = models.BooleanField(default=True)
    sent = models.DateTimeField(null=True)
    key = models.CharField(max_length=64, unique=True)
    
    objects = ExamResponseManager()
    
    ## From allauth.account.models
    #@classmethod
    #def create(cls, extra=None):
    #    key = random_token([extra])
    #    return cls._default_manager.create(key=key)
    
    def send(self, request, email, **kwargs):
        current_site = Site.objects.get_current()
        test_url = reverse("exam_response", args=[self.key])
        test_url = request.build_absolute_uri(test_url)
        ctx = {
            #"user": self.email_address.user,
            "test_url": test_url,
            "current_site": current_site,
            "key": self.key,
        }
        email_template = 'exam/email_test' # "_message.txt" or "_subject.txt" will be added
        get_adapter().send_mail(email_template,
                                email,
                                ctx)
        self.sent = timezone.now()
        self.save()

    def __unicode__(self):
        return self.key[-8:]

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
    rank = models.IntegerField(null=True)
    optional = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.question

class QuestionResponse(models.Model):
    """
    Abstract base class for *Response models.  Subclasses should define a
    "question" field that is a ForeignKey to a *Question model.
    """
    exam_response = models.ForeignKey(ExamResponse)
    
    class Meta:
        abstract = True

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
    response = models.CharField(max_length=RESPONSE_FREE_LENGTH)

    def __unicode__(self):
        return self.response


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
    question = models.ForeignKey(FreeResponseQuestion)
    text = models.CharField(max_length=CHOICE_LENGTH)
    rank = models.IntegerField(null=True)

    def __unicode__(self):
        return self.text


class MultipleChoiceResponse(QuestionResponse):
    """
    Records the response to a multiple choice question.
    """
    question = models.ForeignKey(MultipleChoiceQuestion)
    option = models.ForeignKey(MultipleChoiceOption)

    def __unicode__(self):
        option = MultipleChoiceOption.objects.get(pk=self.option)
        return unicode(option)
