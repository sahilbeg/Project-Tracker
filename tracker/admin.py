from django import forms
from django.contrib import admin
from .models import Project, Account
from django.contrib.auth.models import User
from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html
import random

from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Sprint, Task




class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'description')
    search_fields = ('name', 'description')
    list_filter = ('owner',)
    fields = ('name', 'description', 'owner')

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except Exception as e:
            if 'UNIQUE constraint failed' in str(e):
                raise ValueError("An account with this name already exists.")
            raise e


class AccountOwnerFilter(SimpleListFilter):
    title = 'Account'
    parameter_name = 'account'

    def lookups(self, request, model_admin):
        return [(account.id, account.name) for account in Account.objects.filter(owner=request.user)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(account_id=self.value())
        return queryset


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'account', 'owner', 'participants_initials', 'add_sprint_button')
    search_fields = ('name', 'description')
    list_filter = (AccountOwnerFilter,)
    fields = ('name', 'description', 'account', 'owner', 'participants')

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',),
        }

     # Dynamically set list_display based on user role
    def get_list_display(self, request):
        if request.user.is_superuser:
            # Exclude 'add_sprint_button' for superadmins
            return ('name', 'account', 'owner', 'participants_initials')
        return self.list_display

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'account' in form.base_fields:
            form.base_fields['account'].queryset = Account.objects.filter(owner=request.user)
        if 'participants' in form.base_fields:
            form.base_fields['participants'].queryset = User.objects.exclude(id=request.user.id)
        return form

    def save_model(self, request, obj, form, change):
        if not obj.owner:
            obj.owner = request.user
        super().save_model(request, obj, form, change)
        if obj.owner and obj.owner not in obj.participants.all():
            obj.participants.add(obj.owner)
        obj.save()

    def participants_initials(self, obj):
        initials_list = []
        participants = obj.participants.all()
        if obj.owner and obj.owner not in participants:
            participants = [obj.owner] + list(participants)
        color_list = ['#FF5733', '#33FF57', '#3357FF', '#FF33A1', '#A133FF', '#33FFF6', '#FFC300', '#FF6F61']
        for user in participants:
            name_parts = user.get_full_name().split()
            initials = ''.join([part[0].upper() for part in name_parts if part]) or user.username[0].upper()
            random_color = random.choice(color_list)
            user_type = 'Owner' if user == obj.owner else 'Participant'
            tooltip = f'{user.get_full_name()} ({user_type})'
            initials_list.append(f'<span style="display:inline-block; border-radius:50%; background:{random_color}; '
                                 f'color:#fff; text-align:center; width:25px; height:25px; '
                                 f'line-height:25px; margin:2px; cursor:pointer; transition: transform 0.2s, border 0.2s;" '
                                 f'title="{tooltip}" class="participant-circle">{initials}</span>')
        return format_html(' '.join(initials_list))

    participants_initials.short_description = "Participants"

    def has_change_permission(self, request, obj=None):
        if obj and obj.owner != request.user:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.owner != request.user:
            return False
        return super().has_delete_permission(request, obj)

    def has_view_permission(self, request, obj=None):
        return super().has_view_permission(request, obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        if obj:
            extra_context = extra_context or {}
            extra_context['owner_name'] = obj.owner.get_full_name() if obj.owner else "Unknown"
            extra_context['project'] = obj  # Add the project to the context
        else:
            extra_context = extra_context or {}
            extra_context['owner_name'] = request.user.get_full_name()
        
        # Ensure the project is always included in the navigation
        extra_context['project'] = obj


        return super().change_view(request, object_id, form_url, extra_context)


    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(owner=request.user)

    def add_sprint_button(self, obj):
        return format_html('<a class="sprints-button" href="{}">Sprint Plan</a>',
                        reverse('admin:plan_sprint', args=[obj.pk]))

    add_sprint_button.short_description = 'Add Sprint'



    def get_urls(self):
        """
        Override the get_urls method to add a custom URL for planning the sprint.
        """
        urls = super().get_urls()
        custom_urls = [
            path('plan_sprint/<int:project_id>/', self.admin_site.admin_view(self.plan_sprint), name='plan_sprint'),
        ]
        return custom_urls + urls

    def plan_sprint(self, request, project_id):
        """
        Render the custom view for planning a sprint for a project.
        """
        project = Project.objects.get(pk=project_id)
        
        # Pass project context to the template for consistent navigation
        extra_context = {'project': project}
        
        if request.method == "POST":
            # Handle form submission and create the sprint with tasks
            sprint_name = request.POST.get("sprint_name")
            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")
            tasks = request.POST.getlist("tasks")  # List of task titles

            # Create the Sprint
            sprint = Sprint.objects.create(
                project=project,
                name=sprint_name,
                start_date=start_date,
                end_date=end_date
            )

            # Create tasks
            for task_title in tasks:
                Task.objects.create(
                    sprint=sprint,
                    title=task_title
                )

            messages.success(request, "Sprint created successfully!")
            return HttpResponseRedirect(reverse('admin:tracker_project_change', args=[project.id]))

        # Render the sprint planning form with project context for navigation
        return render(request, 'admin/plan_sprint.html', {'project': project, **extra_context})



admin.site.register(Account, AccountAdmin)
admin.site.register(Project, ProjectAdmin)
