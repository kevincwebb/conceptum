from django.contrib import admin

from .models import (
    Exam,
    ExamResponse,
    FreeResponseQuestion,
    MultipleChoiceOption,
    MultipleChoiceQuestion
)

import reversion


class ExamAdmin(reversion.VersionAdmin):
    pass


# Responses probably don't need to be versioned
class ExamResponseAdmin(admin.ModelAdmin):
    pass


class FreeResponseQuestionAdmin(reversion.VersionAdmin):
    pass


class MultipleChoiceOptionAdmin(reversion.VersionAdmin):
    pass


class MultipleChoiceQuestionAdmin(reversion.VersionAdmin):
    pass

admin.site.register(Exam, ExamAdmin)
admin.site.register(ExamResponse, ExamResponseAdmin)
admin.site.register(FreeResponseQuestion, FreeResponseQuestionAdmin)
admin.site.register(MultipleChoiceOption, MultipleChoiceOptionAdmin)
admin.site.register(MultipleChoiceQuestion, MultipleChoiceQuestionAdmin)
