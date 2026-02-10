from django.urls import path
from .student_api_views import (
    UnifiedDashboardAPI,
    StudentLessonsListAPI,
)

urlpatterns = [
    # Unified endpoints для STUDENT и APPLICANT
    path("", UnifiedDashboardAPI.as_view()),                    # GET /api/dashboard/
    path("lessons/", StudentLessonsListAPI.as_view()),         # GET /api/dashboard/lessons/
]
