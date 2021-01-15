from django.urls import path
from . import views

urlpatterns = [
    #path('autocomplete/', views.job_auto_complete, name='auto_complete'),
    path('job_to_skills/', views.all_job_data, name='all_job_data'),
    path('skills_to_jobs/', views.jobs_from_skill_uuids, name='skills_to_jobs'),
    path('learning_resources/', views.learning_resources, name='learning_resources'),
]