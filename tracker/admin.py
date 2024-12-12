from django.contrib import admin
from .models import Project

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'description')
    search_fields = ('name', 'description')
    list_filter = ('owner',)

admin.site.register(Project, ProjectAdmin)
