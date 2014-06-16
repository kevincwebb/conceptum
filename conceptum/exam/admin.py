from django.contrib import admin

from .models import (
    Exam,
    FreeResponseQuestion,
    MultipleChoiceOption,
    MultipleChoiceQuestion
)

import reversion


class ExamAdmin(reversion.VersionAdmin):
    pass


class FreeResponseQuestionAdmin(reversion.VersionAdmin):
    pass


class MultipleChoiceOptionAdmin(reversion.VersionAdmin):
    pass


class MultipleChoiceQuestionAdmin(reversion.VersionAdmin):
    pass

admin.site.register(Exam, ExamAdmin)
admin.site.register(FreeResponseQuestion, FreeResponseQuestionAdmin)
admin.site.register(MultipleChoiceOption, MultipleChoiceOptionAdmin)
admin.site.register(MultipleChoiceQuestion, MultipleChoiceQuestionAdmin)
