from django.contrib import admin
from .models import *



@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('full_name',)
  
@admin.register(VisitorTag)
class VisitorTagAdmin(admin.ModelAdmin):
    list_display = ('tag_number',)
