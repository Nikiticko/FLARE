from django.urls import path
from .teacher_api_views import (
    TeacherLessonsListCreateAPI,
    TeacherLessonDetailAPI,
    TeacherLessonUpdateAPI,
    TeacherStudentsListAPI,
    TeacherStudentLessonsAPI,
    TeacherStudentByEmailAPI,
    TeacherStudentsAutocompleteAPI,
)

urlpatterns = [
    # Расписание / уроки
    path('lessons/', TeacherLessonsListCreateAPI.as_view()),             # GET/POST
    path('lessons/<int:pk>/', TeacherLessonDetailAPI.as_view()),   # GET
    path('lessons/<int:pk>/update/', TeacherLessonUpdateAPI.as_view()),  # PATCH

    # Журнал учеников
    path('students/', TeacherStudentsListAPI.as_view()),                     # GET список учеников
    path('students/by-email/', TeacherStudentByEmailAPI.as_view()),          # GET поиск ученика по email
    path('students/autocomplete/', TeacherStudentsAutocompleteAPI.as_view()),  # GET автодополнение учеников
    path('students/<int:student_id>/lessons/', TeacherStudentLessonsAPI.as_view()),  # GET журнал по ученику
]
