from django.contrib import admin

from .models import ContributorProfile



class ContributorProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'institution', 'homepage', 'interest_in_devel', 'interest_in_deploy')


# Register your models here.
admin.site.register(ContributorProfile, ContributorProfileAdmin) 