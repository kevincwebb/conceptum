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

class FreeResponseQuestionInLine(admin.TabularInline):
    model = FreeResponseQuestion
    fields = ('content_object',)
    readonly_fields = ('content_object',)
    
class MultipleChoiceQuestionInLine(admin.TabularInline):
    model = MultipleChoiceQuestion
    fields = ('content_object', )
    readonly_fields = ('content_object',)
    
class MultipleChoiceOptionInLine(admin.TabularInline):
    model = MultipleChoiceOption

class ExamAdmin(reversion.VersionAdmin):
    inlines = [FreeResponseQuestionInLine,MultipleChoiceQuestionInLine, ]


# Responses probably don't need to be versioned
class ExamResponseAdmin(admin.ModelAdmin):
    pass


class FreeResponseQuestionAdmin(reversion.VersionAdmin):
    list_display = ('question', 'exam', 'content_type', 'content_object', 'image', 'rank', 'optional', 'pk')
    

class MultipleChoiceOptionAdmin(reversion.VersionAdmin):
    list_display = ('text','question', 'rank', 'pk')


class MultipleChoiceQuestionAdmin(reversion.VersionAdmin):
    list_display = ('question','exam', 'content_type', 'content_object',  'image', 'rank', 'optional', 'pk')
    inlines = [MultipleChoiceOptionInLine]

admin.site.register(Exam, ExamAdmin)
admin.site.register(ExamResponse, ExamResponseAdmin)
admin.site.register(FreeResponseQuestion, FreeResponseQuestionAdmin)
admin.site.register(MultipleChoiceOption, MultipleChoiceOptionAdmin)
admin.site.register(MultipleChoiceQuestion, MultipleChoiceQuestionAdmin)
