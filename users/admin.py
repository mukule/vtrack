from django.contrib import admin
from .models import *


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'email', 'company',
                    'purpose_of_visit', 'host', 'department')
    search_fields = ('full_name', 'phone', 'email',
                     'company', 'purpose_of_visit')


@admin.register(VisitorTag)
class VisitorTagAdmin(admin.ModelAdmin):
    list_display = ('tag_number',)
