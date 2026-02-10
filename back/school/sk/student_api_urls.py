from django.urls import path
from .student_api_views import (
    UnifiedDashboardAPI,
    StudentDashboardAPI,
    StudentCoursesListAPI,
    StudentLessonsListAPI,
    StudentBalanceAPI,
    StudentPaymentsListAPI,
    StudentCreatePaymentAPI,
    StudentSeasonSummaryAPI,
    StudentCreateClientRequestAPI,
)

urlpatterns = [
    path("dashboard/", UnifiedDashboardAPI.as_view()),                    # GET ЛК (STUDENT и APPLICANT)
    path("student-dashboard/", StudentDashboardAPI.as_view()),            # GET ЛК ученика (legacy)
    path("courses/", StudentCoursesListAPI.as_view()),                    # GET список курсов
    path("lessons/", StudentLessonsListAPI.as_view()),                    # GET список уроков
    path("balance/", StudentBalanceAPI.as_view()),                       # GET баланс
    path("payments/", StudentPaymentsListAPI.as_view()),                  # GET история платежей
    path("payments/create/", StudentCreatePaymentAPI.as_view()),          # POST создать платеж
    path("season/summary/", StudentSeasonSummaryAPI.as_view()),          # GET краткая инфа о сезоне
    path("requests/create/", StudentCreateClientRequestAPI.as_view()),    # POST создать обращение к менеджеру
]
