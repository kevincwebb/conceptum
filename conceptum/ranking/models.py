# Model definitions for the ranking app

from django.db import models

from authtools.models import User
from nodemanager.models import ConceptNode, ConceptAtom
from operator import attrgetter

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

    # currently only for binary choice, 
    def get_ranked_items_in_order(self):
        return map(lambda v: v.target, ValueCounter.objects.filter(ranking_process=self))

        
    def close_rank_export_choices(ranking_process):
    
        choices = ranking_process.get_ranked_items_in_order()
        parent_node = ranking_process.parent
        parent_info = parent_node.ci_tree_info
        
        for choice in choices: #choice is a ConceptAtom here

            new_child = ConceptNode(
                ci_tree_info = parent_info,
                parent = parent_node,
                content = choice.text,
            )
            new_child.save()

            #once we have created the new nodes we close the ranking process
            self.status = self.closed
            self.save()
    
            return


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

    target = models.ForeignKey(ConceptAtom)
    ranking_process = models.ForeignKey(RankingProcess)
    value = models.IntegerField()

    def __unicode__(self):
        return "Value " + unicode(self.value) + " of " + unicode(self.target)

    class Meta:
        ordering = ["-value"] #ensures that any queryset of
                              #ValueCounters will be sorted in
                              #descending order
