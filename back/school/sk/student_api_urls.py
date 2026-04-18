from django.urls import path
from .student_api_views import (
    UnifiedDashboardAPI,
    StudentDashboardAPI,
    StudentCoursesListAPI,
    StudentLessonsListAPI,
    StudentBalanceAPI,
    StudentPaymentsListAPI,
    StudentSeasonSummaryAPI,
    StudentCreateClientRequestAPI,
)

urlpatterns = [
    path("dashboard/", UnifiedDashboardAPI.as_view()),
    path("student-dashboard/", StudentDashboardAPI.as_view()),  # legacy
    path("courses/", StudentCoursesListAPI.as_view()),
    path("lessons/", StudentLessonsListAPI.as_view()),
    path("balance/", StudentBalanceAPI.as_view()),
    path("payments/", StudentPaymentsListAPI.as_view()),
    path("season/summary/", StudentSeasonSummaryAPI.as_view()),
    path("requests/create/", StudentCreateClientRequestAPI.as_view()),
]
