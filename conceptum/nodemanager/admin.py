from django.contrib import admin

from .models import ConceptNode

import reversion


class ConceptNodeAdmin(reversion.VersionAdmin):
    pass

admin.site.register(ConceptNode, ConceptNodeAdmin)
