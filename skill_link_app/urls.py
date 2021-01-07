from django.urls import path
from . import views

urlpatterns = [
    #path('autocomplete/', views.job_auto_complete, name='auto_complete'),
    path('job_to_skills/', views.job_title_to_skills, name='job_to_skills'),
    path('skills_to_jobs/', views.jobs_from_skill_uuids, name='skills_to_jobs'),
]