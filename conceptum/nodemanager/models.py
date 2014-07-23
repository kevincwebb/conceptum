from django.db import models

# Used for underlying tree structure
from mptt.models import MPTTModel, TreeForeignKey

from authtools.models import User

# Only one CITreeInfo model can exist per tree. Every node in the CI
# Tree is connected to it. It provides global information, such as:
# -administrators
# -users working on the tree
# -type (whether the tree is the master or not)
# TODO: maybe created by
class CITreeInfo(models.Model):

    admins = models.ManyToManyField(User, related_name='admins')
    users = models.ManyToManyField(User, related_name='users')

    # master tree is loaded on the landing page. there can only be one
    # at any given time.
    is_master = models.BooleanField(default=False)

    def __unicode__(self):
        if self.is_master:
            return "Master Tree Info"
        else:
            return "Tree Info"

    # returns a query set. if it's empty, there is no master tree
    @staticmethod
    def get_master_tree_root():
        master_info = CITreeInfo.objects.filter(is_master=True)
        if master_info:
            nodes = ConceptNode.objects.filter(ci_tree_info=master_info)
            if not nodes:
                print "Error: Master Tree is empty (no root node)"
                return None
            return [node for node in nodes if node.is_root_node()].pop()
        else:
            print "Error: Master Tree does not exist"
            return None


# The ConceptNode functions as a single-type container for all data that
# different node objects might need. We do this instead of inheritance
# because django-mttp can only construct trees of 1 type.
#
# Concept Nodes hold whatever value has been given to them from a
# vote. They can also hold voting processes that, if completed, will
# spawn child nodes whose content contains whatever was chosen from
# the voting process.
class ConceptNode(MPTTModel):

    # gives information about the tree the node belongs to
    ci_tree_info = models.ForeignKey(CITreeInfo)

    # required by mptt
    parent = TreeForeignKey('self', null=True, related_name='children')

    # a node manages individual users
    user = models.ManyToManyField(User)

    #add more types if desired
    # NODECHOICES = (
    #     ('F', 'Free Entry'), #initial brainstorm
    #     ('P', 'Pruning'), #create final voting set
    #     ('R', 'Ranking'), #vote on set and compute optimal choices
    #     ('C', 'Complete'), #no more node-specific edits can be made
    #)
    node_type = models.CharField(max_length=2)
                                 # choices=NODECHOICES,
                                 # default='C',)

    # Whatever content was awarded to this node by the parent voting
    # process
    content = models.TextField(max_length=140)

    def __unicode__(self):
        return self.content

    def get_final_choices(self):
        all_choices =  ConceptAtom.objects.filter(concept_node=self.id)
        return all_choices.filter(final_choice=True)

    def users_contributed_set(self):
        return self.user.all()

    def admin_set(self):
        return self.ci_tree_info.admins.all()

    def is_valid_user(self, user):
        if user in self.ci_tree_info.users.all() or user in self.ci_tree_info.admins.all():
            return True
        else:
            return False

    def is_active(self):
        if not self.node_type == 'C':
            return True
        else:
            return False

    # easy way of doing it for now, probably want to override __iter__
    # of node_type for a cleaner solution that scales and maybe break
    # up into separate functions
    def transition_node_state(self):

        #update node_type
        if self.node_type == 'F':
            self.node_type = 'P'
        elif self.node_type == 'P':
            self.node_type = 'R'
        elif self.node_type == 'R':
            self.node_type = 'C'

        self.save()

        #transition means a new voting process has begun so we scrub
        #the contributed_users list
        self.user.clear()

        return

    def is_stage_finished(self):
        if list(self.users_contributed_set()) == list(self.ci_tree_info.users.all()):
            return True
        else:
            return False


# Atoms are entered by the user and are meant to represent
# topics/concepts/module names that altogether will form a
# hierarchical representation of a CI. They each link to one node and
# one user. "Final Choice" represents whether or not an atom has
# passed the pruning process.

MAX_LENGTH = 140

class ConceptAtom(models.Model):

    concept_node = models.ForeignKey(ConceptNode)
    user = models.ForeignKey(User)

    text = models.CharField(max_length=MAX_LENGTH)
    final_choice = models.BooleanField(default=False)
    merged_atoms = models.ForeignKey(ConceptAtom)

    def __unicode__(self):
        return self.text
