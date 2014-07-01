from django.db import models

# Used to allow inherited nodes to exist on a tree
from django.contrib.contenttypes import ContentType
from django.contrib.contenttypes import generic

# Used for underlying tree structure
from mptt.models import MPTTModel, TreeForeignKey

from django.contrib.auth.models import User


# Create your models here.

class ConceptAtom(models.Model):
    text = models.CharField(max_length=140) #twitter
    freeentrynode = models.ForeignKey(FreeEntryNode)
    
class BaseNode(MPTTModel):
    name = (
        ('F', 'Free Entry'),
        ('P', 'Pruning'),
        ('R', 'Ranking'),
    ) # add more types if desired

    parent = TreeForeignKey('self', null=True, related_name='children')

    # Content Type holds the actual node object. BaseNode is a wrapper
    # around different kinds of nodes because mptt requires every
    # object in a tree to be the same type
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')


class FreeEntryNode(models.Model):

    # a node manages a list of users
    user = models.ManyToManyFields(User)



