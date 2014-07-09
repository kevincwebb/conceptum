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

    # TODO: Add Methods

# Atoms are entered by the user and are meant to represent
# topics/concepts/module names that altogether will form a
# hierarchical representation of a CI. They each link to one node and
# one user. "Final Choice" represents whether or not an atom has
# passed the pruning process.
class ConceptAtom(models.Model):

    MAX_LENGTH = 140

    concept_node = models.ForeignKey(ConceptNode)
    user = models.ForeignKey(User)

    text = models.CharField(max_length=MAX_LENGTH)
    final_choice = models.BooleanField(default=False)

    @classmethod
    def create_atom(self, concept_node, user, text="", final_choice=False):

        #check text
        if len(text) > MAX_LENGTH:
            print "Error: text entered is too long"
            return

        #check for valid user
        concept_users = concept_node.ci_tree_info.users.all()
        if user not in concept_users:
            print "Error: user not associated with concept tree"
            return

        return ConceptAtom(concept_node, user, text, final_choice)
