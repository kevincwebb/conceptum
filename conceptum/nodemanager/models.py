from django.db import models

# Used for underlying tree structure
from mptt.models import MPTTModel, TreeForeignKey

from django.contrib.auth.models import User

# Only one CITreeInfo model can exist per tree. Every node in the CI
# Tree is connected to it. It provides global information, such as:
# -administrators
# -users working on the tree
# -type (whether the tree is the master or not)
# TODO: maybe created by
class CITreeInfo(models.Model):

    admins = ManyToManyField(User)
    users = ManyToManyField(User)

    # master tree is loaded on the landing page. there can only be one
    # at any given time.
    ismaster = models.BooleanField(default=False)
    

# The ConceptNode functions as a single-type container for all data that
# different node objects might need. We do this instead of inheritance
# because django-mttp can only construct trees of 1 type.
class ConceptNode(MPTTModel):

    # gives information about the tree the node belongs to
    citreeinfo = ForeignKey(CITreeInfo)
        
    # required by mptt
    parent = TreeForeignKey('self', null=True, related_name='children')

    # a node manages individual users
    user = models.ManyToManyField(User)

    nodetype = (
        ('F', 'Free Entry'),
        ('P', 'Pruning'),
        ('R', 'Ranking'),
        ('A', 'Active'),
    ) #add more types (with necessary fields) if desired. make sure
      #the fields are added to the concept node itself, or accessed
      #via ForeignKey.


    # TODO: Add Methods

# These are entered by the user and are meant to represent
# topics/concepts/module names that altogether will form a
# hierarchical representation of a CI. They each link to one node and
# one user. "Final Choice" represents whether or not an atom has
# passed the pruning process.
class ConceptAtom(models.Model):
    
    conceptnode = models.ForeignKey(ConceptNode)
    user = models.ForeignKey(User)

    text = models.CharField(max_length=140)
    finalChoice = models.BooleanField(default=False)
    rank = None #TODO: figure it out
