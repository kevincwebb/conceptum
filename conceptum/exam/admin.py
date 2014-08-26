from django.contrib import admin

from .models import (
    Exam,
    ExamResponse,
    FreeResponseQuestion,
    FreeResponseResponse,
    MultipleChoiceOption,
    MultipleChoiceQuestion,
    MultipleChoiceResponse,
)

import reversion


class ExamAdmin(reversion.VersionAdmin):
    pass

# Responses probably don't need to be versioned
class ExamResponseAdmin(admin.ModelAdmin):
    #list_display = ('is_available',)
    pass

class FreeResponseQuestionAdmin(reversion.VersionAdmin):
    pass

class FreeResponseResponseAdmin(admin.ModelAdmin):
    #list_display = ('exam_response', 'question')
    pass

class MultipleChoiceOptionAdmin(reversion.VersionAdmin):
    pass

class MultipleChoiceQuestionAdmin(reversion.VersionAdmin):
    pass

class MultipleChoiceResponseAdmin(admin.ModelAdmin):
    pass

admin.site.register(Exam, ExamAdmin)
admin.site.register(ExamResponse, ExamResponseAdmin)
admin.site.register(FreeResponseQuestion, FreeResponseQuestionAdmin)
admin.site.register(FreeResponseResponse, FreeResponseResponseAdmin)
admin.site.register(MultipleChoiceOption, MultipleChoiceOptionAdmin)
admin.site.register(MultipleChoiceQuestion, MultipleChoiceQuestionAdmin)
admin.site.register(MultipleChoiceResponse, MultipleChoiceResponseAdmin)
