# Model definitions for the ranking app

from django.db import models

from authtools.models import User
from operator import attrgetter
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

import nodemanager.models #full namespace to avoid circular import
                          #(hopefully)

class RankingProcess(models.Model):
    """
    This model contains all the necessary information that determines
    a ranking process.

    -Choices: a set of objects we are voting on (currently concept atoms)
    
    -Parent: what this ranking process is attached to (currently a
    concept node. Note that this "parent" field is how we figure out
    who is voting and administrating, since that information is
    available in the concept node's CI Tree Info model).

    -Value Choice: The ranking system (currently just binary is implemented)

    -Status: one of Not Initialized/In Progress/Closed
    """

    # ranking processes can be attached to any kind of object.
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    parent = generic.GenericForeignKey('content_type', 'object_id')

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

    #possible ranking states
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

    def get_rank_choices(self):
        """
        This function returns a list of every item that can be ranked by
        the Ranking Process by finding everything attached to its
        Value Counters.

        Note: due to the metaclass ordering enforced in the
        ValueCounter class, this function (for now) will return the
        items in descending order according to their integer
        value. This "feature" and will fall apart if more complex
        notions of value are created for concept atoms. Consider the
        use of this function to return items in order as already
        "deprecated"
        """

        return map(lambda vc: vc.target, ValueCounter.objects.filter(ranking_process=self))

    def __unicode__(self):
        return "Ranking Process of " + unicode(self.parent)


        
class ValueCounter(models.Model):
    """
    The Value Counter model stores voting information entered by the
    user. There is one counter attached to each object in the voting
    set.

    The value counter currently has this information:

    - target: the object whose value it tracks
    
    - ranking process: the parent ranking process this counter belongs
      to

    - value: the actual value it holds. This can theoretically be
      expanded.
    """

    # value counters can be attached to any object
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    target = generic.GenericForeignKey('content_type', 'object_id')

    ranking_process = models.ForeignKey(RankingProcess)
    value = models.IntegerField()

    def __unicode__(self):
        return "Value " + unicode(self.value) + " of " + unicode(self.target)

    class Meta:
        ordering = ["-value"] #ensures that any queryset of
                              #ValueCounters will be sorted in
                              #descending order
