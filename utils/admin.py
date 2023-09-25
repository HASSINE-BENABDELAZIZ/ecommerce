from django.contrib import admin

from .models import BreadcrumbModel


class BreadcrumbModelAdmin(admin.ModelAdmin):
    list_display = (
        'url', 'utility'
    )
    search_fields = ['url', 'utility']


admin.site.register(BreadcrumbModel, BreadcrumbModelAdmin)
