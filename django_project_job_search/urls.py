from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('skill_link/', include('skill_link_app.urls')),
]
