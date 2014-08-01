from django.contrib import admin
from django.contrib.contenttypes.generic import GenericTabularInline, GenericStackedInline 

from .models import (
    Exam,
    ExamResponse,
    FreeResponseQuestion,
    MultipleChoiceOption,
    MultipleChoiceQuestion
)

import reversion

class FreeResponseInLine(admin.TabularInline):
    model = FreeResponseQuestion
    fields = ('content_object',)
    readonly_fields = ('content_object',)
    
class ExamAdmin(reversion.VersionAdmin):
    inlines = [FreeResponseInLine,]


# Responses probably don't need to be versioned
class ExamResponseAdmin(admin.ModelAdmin):
    pass


class FreeResponseQuestionAdmin(reversion.VersionAdmin):
    list_display = ('exam', 'content_type', 'content_object', 'question', 'image', 'rank', 'optional',)
    

class MultipleChoiceOptionAdmin(reversion.VersionAdmin):
    pass


class MultipleChoiceQuestionAdmin(reversion.VersionAdmin):
    pass

admin.site.register(Exam, ExamAdmin)
admin.site.register(ExamResponse, ExamResponseAdmin)
admin.site.register(FreeResponseQuestion, FreeResponseQuestionAdmin)
admin.site.register(MultipleChoiceOption, MultipleChoiceOptionAdmin)
admin.site.register(MultipleChoiceQuestion, MultipleChoiceQuestionAdmin)
