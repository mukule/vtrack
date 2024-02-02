from django.contrib import admin
from .models import *



@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('full_name',)
  
@admin.register(VisitorTag)
class VisitorTagAdmin(admin.ModelAdmin):
    list_display = ('tag_number',)



@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'rate', 'comments', 'created_at')
    list_filter = ('visitor', 'rate')
    search_fields = ('visitor__full_name', 'rate__name', 'comments')
    date_hierarchy = 'created_at'