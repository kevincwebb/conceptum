from django.contrib import admin

from .models import ContributorProfile



class ContributorProfileAdmin(admin.ModelAdmin):
	#fields = ['pub_date','question']
	#fieldsets = [
	#	(None, {'fields': ['question']}),
	#	('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
	#]
	#inlines = [ChoiceInline]
	list_display = ('user', 'homepage', 'interest_in_devel', 'interest_in_deploy')
	#list_filter = ['pub_date']
	#search_fields = ['question']

# Register your models here.
admin.site.register(ContributorProfile, ContributorProfileAdmin) 