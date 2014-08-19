from django.db import models

from authtools.models import User
from nodemanager.models import ConceptNode, ConceptAtom


class RankingProcess(models.Model):

    choices = models.ManyToManyField(ConceptAtom)
    parent = models.ForeignKey(ConceptNode)

    #let's overcommit to following the Django website example (for
    #now) since charfield choices didn't really work the last time
    binary = 'BIN'
    hierarchical = 'HIE'
    #more can be added later if desired

    VALUE_CHOICES = (
        (binary, 'Binary Choice'),
        (hierarchical, 'Hierarchy'),
    )
    value_choices = models.CharField(max_length=3,
                                    choices=VALUE_CHOICES,
                                    default=binary)

    not_initialized = 'N'
    in_progress = 'I'
    closed = 'C'
    STATE_CHOICES = (
        (not_initialized,'Not Initialized'),
        (in_progress, 'In Progress'),
        (closed, 'Closed')
    )
    status = models.CharField(max_length=1,
                             choices=STATE_CHOICES,
                             default=not_initialized)


class ValueCounter(models.Model):

    target = models.ForeignKey(ConceptAtom)
    ranking_process = models.ForeignKey(RankingProcess)
    value = models.IntegerField()
