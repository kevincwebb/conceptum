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

    target = models.ForeignKey(ConceptAtom)
    ranking_process = models.ForeignKey(RankingProcess)
    value = models.IntegerField()

    def __unicode__(self):
        return "Value " + unicode(self.value) + " of " + unicode(self.target)

    class Meta:
        ordering = ["-value"] #ensures that any queryset of
                              #ValueCounters will be sorted in
                              #descending order
