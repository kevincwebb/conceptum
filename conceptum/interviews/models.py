from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse

class DummyConcept(models.Model):
    """
    this model is temporary.  See get_concept_list() below
    """
    name = models.CharField(max_length=31, unique=True)
    
    def __str__(self):
        return self.name


def get_concept_list():
    """
    this method is temporary.  Its anticipated replacement is a method in the
    ConceptNode class that will return a list of leaf nodes.
    """

    DummyConcept.objects.get_or_create(name='Concept A')
    DummyConcept.objects.get_or_create(name='Concept B')
    DummyConcept.objects.get_or_create(name='Concept C')
    DummyConcept.objects.get_or_create(name='Concept D')
    return DummyConcept.objects.all()


class Interview(models.Model):
    """
    Model for uploading interviews with experts or students.
    The interview model only has fields for interviewee, date, and interviewer.
    Responses are stored in the Excerpt model which has a many-to-one relationship
    with the Interview model and can be accessed via Interview.objects.excerpt_set.all().
    See https://docs.djangoproject.com/en/1.6/topics/db/queries/#following-relationships-backward
    """
    
    interviewee = models.CharField(max_length=255)
    
    date_of_interview = models.DateField()
    
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    
    date_uploaded = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return "Interview with {person} on {date}".format(
            person=self.interviewee, date=self.date_of_interview)
    
    def get_absolute_url(self):
        return reverse('interview_detail', kwargs={'pk': self.pk})
    

class Excerpt(models.Model):
    """
    Excerpts are used in interviews to store interviewee responses.  Each excerpt is associated
    with a topic (this will probably be a Concept/ConceptNode) and an interview. 
    """

    # Fields that relate to some sort of Topic, probably a ConceptNode
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    interview = models.ForeignKey(Interview)
    
    response = models.TextField()