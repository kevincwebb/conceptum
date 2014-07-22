from django.contrib import admin

from .models import Interview, Excerpt


class InterviewAdmin(admin.ModelAdmin):
	list_display = ('interviewee', 'date_of_interview', 'uploaded_by', 'date_uploaded')


class ExcerptAdmin(admin.ModelAdmin):
	list_display = ('content_object', 'interview', 'response', 'object_id')


admin.site.register(Interview, InterviewAdmin)
admin.site.register(Excerpt, ExcerptAdmin)