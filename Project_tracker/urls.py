# project_tracker/urls.py

from django.contrib import admin
from django.urls import path, include  # Import 'include'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tracker/', include('tracker.urls')),  # Include URLs from the tracker app
]

