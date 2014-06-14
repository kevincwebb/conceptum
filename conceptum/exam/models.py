from django.db import models

# import reversion

# Constants
EXAM_NAME_LENGTH = 100
EXAM_DESC_LENGTH = 500
QUESTION_LENGTH = 1000
CHOICE_LENGTH = 500
RESPONSE_FREE_LENGTH = 2000


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
    question = models.CharField(max_length=QUESTION_LENGTH)
    image = models.ImageField(upload_to=question_imageupload_to, blank=True)
    rank = models.IntegerField(null=True)
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


class FreeResponseResponse(models.Model):
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


class MultipleChoiceResponse(models.Model):
    """
    Records the response to a multiple choice question.
    """
    question = models.ForeignKey(MultipleChoiceQuestion)
    option = models.ForeignKey(MultipleChoiceOption)

    def __unicode__(self):
        option = MultipleChoiceOption.objects.get(pk=self.option)
        return unicode(option)
