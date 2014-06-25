#For a regular list of items without votes from your model use the following:
item_list_no_score = Items.objects.all()

#For a list with scores that can be customized with use the following:
item_list_unordered_with_scores = Items.objects_with_scores.all()
#to customize the order by a field unique to your model. So something like this:
item_list_unordered_with_scores = Items.objects_with_scores.all().order_by(-date_created)

#To obtain a list of items sorted by vote counts like (1,0,-1) like Reddit:
item_list_ordered__scores = Items.sort_by_score.all()