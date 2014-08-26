import hashlib
import random

from django.db import models
from django.contrib.contenttypes.models import ContentType

#from .models import FreeResponseResponse, MultipleChoiceResponse

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