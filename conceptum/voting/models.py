from django.db import models
from qhonuskan_votes.models import VotesField

class MyModel(models.Model):
    votes = VotesField()
    # Add objects before all other managers to avoid issues mention in http://stackoverflow.com/a/4455374/1462141
    objects = models.Manager()

    #For just a list of objects that are not ordered that can be customized.
    objects_with_scores = ObjectsWithScoresManager()

    #For objects ordered by score.
    sort_by_score = SortByScoresManager()

