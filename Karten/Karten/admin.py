from django.contrib import admin
from Karten.models import *


class KartenStackAdmin(admin.ModelAdmin):

    list_display = ('owner', 'name', 'creation_date')

admin.site.register(KartenStack, KartenStackAdmin)

class KartenUserAdmin(admin.ModelAdmin):

    list_display = ('first_name', 'last_name', 'external_service')

admin.site.register(KartenUser, KartenUserAdmin)
