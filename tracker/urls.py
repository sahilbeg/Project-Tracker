from django.urls import path
from . import views  # Import your views file
from .views import search_users

urlpatterns = [
    # Account-related URLs
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/<int:account_id>/create_project/', views.create_project, name='create_project'),

    # Sprint-related URLs
    path('admin/tracker/sprint/delete/<int:pk>/', views.delete_sprint, name='tracker_sprint_delete'),
    path('project/<int:project_id>/sprint/save/', views.save_sprint, name='save_sprint'),
    path('project/<int:project_id>/sprint/check_exists/', views.check_sprint_exists, name='check_sprint_exists'),

    # Task-related URLs
    path('task/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('task/<int:task_id>/update/', views.update_task, name='update_task'),
    path('task/add/', views.add_task, name='add_task'),

    path('api/search-users/', search_users, name='search_users'),
    path('get_user_suggestions/<int:project_id>/', views.get_user_suggestions, name='get_user_suggestions'),

    path('save-task/', views.save_task, name='save_task'),
    
]
