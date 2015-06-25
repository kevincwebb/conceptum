from django.contrib import admin
from django.contrib.contenttypes.generic import GenericTabularInline, GenericStackedInline 

from .models import (
    Exam,
    ResponseSet,
    ExamResponse,
    FreeResponseQuestion,
    FreeResponseResponse,
    MultipleChoiceOption,
    MultipleChoiceQuestion,
    MultipleChoiceResponse,
)

import reversion

"""
Warning! For versioning to work correctly, if you want to register a model with
reversion.VersionAdmin, do not also register it as a ModelAdmin or Inline.
(this message brought to you by many hours of frustration with django-reversion)
"""

#class FreeResponseQuestionInLine(admin.TabularInline):
#    model = FreeResponseQuestion
#    fields = ('content_object',)
#    readonly_fields = ('content_object',)
# 
#    
#class MultipleChoiceQuestionInLine(admin.TabularInline):
#    model = MultipleChoiceQuestion
#    fields = ('content_object', )
#    readonly_fields = ('content_object',)
    
    
class MultipleChoiceOptionInLine(admin.TabularInline):
    model = MultipleChoiceOption
    list_display = ('text','question', 'rank', 'pk')


class ExamAdmin(admin.ModelAdmin):
    fields = ('name','description')
    #inlines = [FreeResponseQuestionInLine,MultipleChoiceQuestionInLine, ]


class FreeResponseQuestionAdmin(reversion.VersionAdmin):
    list_display = ('question', 'exam', 'content_type', 'content_object', 'image', 'rank', 'optional', 'pk')


class MultipleChoiceQuestionAdmin(reversion.VersionAdmin):
    list_display = ('question','exam', 'content_type', 'content_object',  'image', 'rank', 'optional', 'pk')
    inlines = [MultipleChoiceOptionInLine]


#class MultipleChoiceOptionAdmin(reversion.VersionAdmin):
#    list_display = ('text','question', 'rank', 'pk')


class ResponseSetAdmin(admin.ModelAdmin):
    pass


class ExamResponseAdmin(admin.ModelAdmin):
    pass


class MultipleChoiceResponseAdmin(admin.ModelAdmin):
    pass


class FreeResponseResponseAdmin(admin.ModelAdmin):
    pass


admin.site.register(Exam, ExamAdmin)
admin.site.register(FreeResponseQuestion, FreeResponseQuestionAdmin)
admin.site.register(MultipleChoiceQuestion, MultipleChoiceQuestionAdmin)
#admin.site.register(MultipleChoiceOption, MultipleChoiceOptionAdmin)
admin.site.register(ResponseSet, ResponseSetAdmin)
admin.site.register(ExamResponse, ExamResponseAdmin)
admin.site.register(FreeResponseResponse, FreeResponseResponseAdmin)
admin.site.register(MultipleChoiceResponse, MultipleChoiceResponseAdmin)