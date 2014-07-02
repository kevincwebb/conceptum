from django.db import models

# Used to allow inherited nodes to exist on a tree
from django.contrib.contenttypes import ContentType
from django.contrib.contenttypes import generic
# Used for underlying tree structure
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User



# These are entered by the user and are meant to represent
# topics/concepts/module names that altogether will form a
# hierarchical representation of a CI. They each link to one node and
# one user. "Final Choice" represents whether or not an atom has
# passed the pruning process.
class ConceptAtom(models.Model):
    conceptnode = models.ForeignKey(ConceptNode)
    user = models.ForeignKey(User)

    text = models.CharField(max_length=140) #twitter
    finalChoice = models.BooleanField(default=False)
    rank = None #TODO: figure it out


# The BaseNode functions as a single-type container for all data that
# different node objects might need. We do this instead of inheriting
# because django-mttp can only construct trees of 1 type.
class ConceptNode(MPTTModel):
    nodetype = (
        ('F', 'Free Entry'),
        ('P', 'Pruning'),
        ('R', 'Ranking'),
        ('A', 'Active'),
    ) #add more types (with necessary fields)if desired. You can't
      #inherit this node, since mptt trees only work with one kind of
      #object (due to dependency on django's QuerySet API)

    parent = TreeForeignKey('self', null=True, related_name='children')

    # a node manages individual users
    user = models.ManyToManyFields(User)

    # TODO: Add Methods
                
    



    


