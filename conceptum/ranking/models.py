from django.db import models

from authtools.models import User
from nodemanager.models import ConceptNode, ConceptAtom
from operator import attrgetter

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

    # currently only for binary choice, 
    def get_ranked_items_in_order(self):
        return map(lambda v: v.target, ValueCounter.objects.filter(ranking_process=self))

    def __unicode__(self):
        return "Ranking Process of " + unicode(self.parent)


class ValueCounter(models.Model):

    target = models.ForeignKey(ConceptAtom)
    ranking_process = models.ForeignKey(RankingProcess)
    value = models.IntegerField()

    def __unicode__(self):
        return "Value " + unicode(self.value) + " of " + unicode(self.target)

    class Meta:
        ordering = ["-value"] #ensures that any queryset of
                              #ValueCounters will be sorted in
                              #descending order
