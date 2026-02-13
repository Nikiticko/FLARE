from django.urls import path
from .admin_api_views import (
    AdminUserListAPI,
    AdminUserDetailAPI,
    AdminUserByEmailAPI,
    AdminSetRoleAPI,
    AdminResetPasswordAPI,
    AdminPaymentListAPI,
    AdminPaymentConfirmAPI,
    AdminBalanceGetAPI,
    AdminLessonListAPI,
    AdminLessonUpdateAPI,
    AdminLessonDebitAPI,
    AdminAuditLogListAPI,
    AdminCourseListCreateAPI,
    AdminCourseDetailAPI,
    AdminLessonPriceAPI,
)

urlpatterns = [
    # USERS
    path("users/", AdminUserListAPI.as_view()),                 # GET список
    path("users/by-email/", AdminUserByEmailAPI.as_view()),     # GET поиск по email
    path("users/<int:pk>/", AdminUserDetailAPI.as_view()),      # GET/PATCH/DELETE
    path("users/<int:pk>/set-role/", AdminSetRoleAPI.as_view()),  # PATCH {"role": "TEACHER"}
    path("users/<int:pk>/reset-password/", AdminResetPasswordAPI.as_view()),  # POST сброс пароля

    # PAYMENTS / BALANCE
    path("payments/", AdminPaymentListAPI.as_view()),                       # GET/POST
    path("payments/<int:pk>/confirm/", AdminPaymentConfirmAPI.as_view()),   # POST {"lessons_to_add": 4}
    path("students/<int:student_id>/balance/", AdminBalanceGetAPI.as_view()),

    # LESSONS
    path("lessons/", AdminLessonListAPI.as_view()),                         # GET/POST
    path("lessons/<int:pk>/", AdminLessonUpdateAPI.as_view()),            # PATCH
    path("lessons/<int:pk>/debit/", AdminLessonDebitAPI.as_view()),         # POST {"mark_done": true}

    # AUDIT LOG
    path("audit/", AdminAuditLogListAPI.as_view()),                         # GET (search/order)

    # COURSES
    path("courses/", AdminCourseListCreateAPI.as_view()),                   # GET список / POST создать
    path("courses/<int:pk>/", AdminCourseDetailAPI.as_view()),             # GET/PATCH/DELETE

    # SETTINGS
    path("settings/lesson-price/", AdminLessonPriceAPI.as_view()),
]
