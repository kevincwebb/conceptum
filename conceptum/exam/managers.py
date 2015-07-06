import hashlib
import random

from django.db import models
from django.contrib.contenttypes.models import ContentType

#from .models import FreeResponseResponse, MultipleChoiceResponse


class FreeResponseManager(models.Manager):
    use_for_related_fields = True
    
    def get_queryset(self):
        return super(FreeResponseManager, self).get_queryset().filter(is_multiple_choice=False)
    
    def create(self, **kwargs):
        kwargs.update({'is_multiple_choice':False})
        return super(FreeResponseManager, self).create(**kwargs)


class MultipleChoiceManager(models.Manager):
    use_for_related_fields = True
    
    def get_queryset(self):
        return super(MultipleChoiceManager, self).get_queryset().filter(is_multiple_choice=True)
    
    def create(self, **kwargs):
        kwargs.update({'is_multiple_choice':True})
        return super(MultipleChoiceManager, self).create(**kwargs)


def random_token(extra=None, hash_func=hashlib.sha256):
    """
    copied from allauth.account.utils
    """
    if extra is None:
        extra = []
    bits = extra + [str(random.SystemRandom().getrandbits(512))]
    return hash_func("".join(bits).encode('utf-8')).hexdigest()

class ExamResponseManager(models.Manager):
    
    def create(self, **kwargs):
        key = random_token(['extra_string'])
        return super(ExamResponseManager,self).create(key=key, **kwargs)