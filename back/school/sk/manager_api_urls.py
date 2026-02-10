from django.urls import path
from .manager_api_views import (
    ManagerClientsListAPI,
    ManagerUserByEmailAPI,
    ManagerUsersAutocompleteAPI,
    ManagerLessonsListCreateAPI, ManagerLessonUpdateAPI, ManagerLessonCancelAPI, ManagerLessonDebitAPI,
    ManagerPaymentsListCreateAPI, ManagerPaymentConfirmAPI, ManagerStudentBalanceAPI, ManagerStudentBalanceUpdateAPI,
    ManagerClientRequestsListAPI, ManagerClientRequestUpdateAPI,
)

urlpatterns = [
    # Клиенты
    path('clients/', ManagerClientsListAPI.as_view()),
    
    # Поиск пользователя по email (должен быть перед lessons, чтобы не конфликтовал)
    path('users/by-email/', ManagerUserByEmailAPI.as_view()),  # GET поиск по email
    path('users/autocomplete/', ManagerUsersAutocompleteAPI.as_view()),  # GET автодополнение

    # Расписание / Уроки
    path('lessons/', ManagerLessonsListCreateAPI.as_view()),          # GET/POST
    path('lessons/<int:pk>/', ManagerLessonUpdateAPI.as_view()),      # PATCH
    path('lessons/<int:pk>/cancel/', ManagerLessonCancelAPI.as_view()),  # POST
    path('lessons/<int:pk>/debit/', ManagerLessonDebitAPI.as_view()),    # POST

    # Платежи и Баланс
    path('payments/', ManagerPaymentsListCreateAPI.as_view()),        # GET/POST
    path('payments/<int:pk>/confirm/', ManagerPaymentConfirmAPI.as_view()),  # POST
    path('students/<int:student_id>/balance/', ManagerStudentBalanceAPI.as_view()),  # GET
    path('students/<int:student_id>/balance/update/', ManagerStudentBalanceUpdateAPI.as_view()),  # PATCH

    # Обращения клиентов
    path('requests/', ManagerClientRequestsListAPI.as_view()),         # GET список обращений
    path('requests/<int:pk>/', ManagerClientRequestUpdateAPI.as_view()),  # PATCH изменить статус
]
