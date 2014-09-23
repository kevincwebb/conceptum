# Defines the models for the nodemanager class

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey #for tree structure
from authtools.models import User


class CITreeInfo(models.Model):
    """
    CI Tree Info defines parameters that hold true throughout an
    entire concept hierarchy. These parameters are:
    
    - users (can add and vote on new concepts)

    - administrators (user privileges, +merge, +set boundaries, +force
      vote close)

    - type: whether or not this tree is the "master" -- or tree with
      the highest user approval rating
    """

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

    @staticmethod
    def get_master_tree_root():
        """
        This function the root node of the master concept hierarchy. There
        should only be one of them.
        """

        master_info = CITreeInfo.objects.filter(is_master=True)
        if master_info:
            nodes = ConceptNode.objects.filter(ci_tree_info=master_info)
            if not nodes:
                print "Error: Master Tree is empty (no root node)"
                return None

            #if there are multiple master trees (which there
            #shouldn't), just return the first one
            return [node for node in nodes if node.is_root_node()].pop()
        else:
            print "Error: Master Tree does not exist"
            return None


# All concepts/topics/questions entered can't be longer than
# this. #thankstwitter
MAX_LENGTH = 140


class ConceptNode(MPTTModel):
    """
    Each node manages the canonical process for creating a modular
    concept inventory.
    
    1. Everyone brainstorms potential concepts (simple text)
    2. The raw list is pruned by an admin to produce a final set.
    3. everyone votes on this set to determine which are selected.

    Because our concept hierarchy is meant to be modular, this process
    will occur multiple times: topics have modules, modules have
    concepts, and concepts have questions.

    A Concept Node stores the following information necessary for this
    process:

    - CI Tree Info: which overall hierarchy it is attached to
      (concepts don't know about neighbors, only children.
    
    - User: tracks which users have visited the concept node. Resets
      when the node changes state

    - Node Type: The state of the node (currently: "Free Entry",
      "Merge", "Rank" or "Closed")

    - Content: The text that contains data relevant to the concept
      hierarchy. This might be a topic/module name, a concept, or
      question text.
    """

    ci_tree_info = models.ForeignKey(CITreeInfo)

    # required by mptt
    parent = TreeForeignKey('self', null=True, related_name='children')

    user = models.ManyToManyField(User) #multiple users can visit one
                                        #node

    #temporary arbitrary charfield (meant to be choices)
    node_type = models.CharField(max_length=2)

    content = models.TextField(max_length=140)

    def __unicode__(self):
        return self.content

    def get_final_choices(self):
        """
        Get all final choices, i.e. those determined to be in the final
        set after a merge.
        """

        all_choices =  ConceptAtom.objects.filter(concept_node=self.id)
        return all_choices.filter(final_choice=True)

    def users_contributed_set(self):
        """
        Return all the users who have visited this node thus far.
        """
        return self.user.all()

    def admin_set(self):
        """
        Return all the admins of this node.
        """
        return self.ci_tree_info.admins.all()

    def is_valid_user(self, user):
        """
        Given a user, determine if the user is in the node's set of
        visitors. (this is admin-inclusive)
        """

        if user in self.ci_tree_info.users.all() or user in self.ci_tree_info.admins.all():
            return True
        else:
            return False

    def is_active(self):
        """
        Returns whether or not the node is has finished all processes.
        """
        
        if not self.node_type == 'C':
            return True
        else:
            return False

    # easy way of doing it for now, probably want to override __iter__
    # of node_type for a cleaner solution that scales and maybe break
    # up into separate functions
    def transition_node_state(self):
        """
        Advance the state of a node to the next logical one. (Note that
        this resets the visited users field to empty.)
        """

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

    def check_users_visited(self):
        """
        Check if all the users have visited the node.
        """
        
        if list(self.users_contributed_set()) == list(self.ci_tree_info.users.all()):
            return True
        else:
            return False

    def check_admin_visited(self):
        """
        Check if an admin has visited the node
        """
        
        if not set(self.admin_set()).isdisjoint(set(self.users_contributed_set())):
            return True
        else:
            return False

    def is_stage_finished(self):
        """
        Given a node in a particular state, check if it is finished.
        """

        if self.node_type == 'F' or self.node_type == 'R':
            return self.check_users_visited()
        elif self.node_type == 'P':
            return self.check_admin_visited()


class ConceptAtom(models.Model):
    """
    A Concept Atom serves as a container for a concept and is passed
    around in the implementations for "free entry", "merging", and
    "ranking".

    A Concept Atom has the following information:

    - Concept Node: the parent node process that this atom belongs to
    - User: tracks which user created the atom
    - Text: The concept/topic/module name/question content itself
    - Final Choice: whether or not this atom is in the post-merge set
    - Merged Atoms: what concept atoms were merged under this one
    """

    concept_node = models.ForeignKey(ConceptNode)

    # only one user can create a node
    user = models.ForeignKey(User)

    text = models.CharField(max_length=MAX_LENGTH)

    final_choice = models.BooleanField(default=False)

    # many atoms can only be merged under one single atom
    merged_atoms = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.text

    @staticmethod
    def get_unmerged_atoms(node):
        """ Return all atoms that have not been merged. """

        return ConceptAtom.objects.filter(concept_node=node).filter(merged_atoms=None).exclude(final_choice=True)

    @staticmethod
    def get_final_atoms(node):
        """
        Get all final choices, i.e. those determined to be in the final
        set after a merge.

        NOTE: this is a redundant method; ConceptNode already has a
        method that does this (I think)
        """

        return ConceptAtom.objects.filter(concept_node=node).filter(final_choice=True)

    def add_merge_atoms(self, atoms):
        """
        Given a queryset of atoms, add them to/merge them under this atom.
        """

        for atom in atoms:
            atom.merged_atoms = self
            atom.save()

    def get_dependent_atoms(self):
        """ Get all atoms merged under this one."""
        
        return ConceptAtom.objects.filter(merged_atoms__pk=self.pk)
