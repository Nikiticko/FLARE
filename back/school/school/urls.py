from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),

    # API авторизации /api/auth/login/, /api/auth/register/ и т.д.
    path('api/', include('accounts.api_urls', namespace='accounts_api')),

    # HTML-страницы (если используются, можно оставить как есть)
    path('', include('accounts.urls', namespace='accounts')),

    # API админа /api/admin/...
    path('api/admin/', include('sk.admin_api_urls')),

    # API менеджера /api/manager/...
    path('api/manager/', include('sk.manager_api_urls')),

    # API учителя /api/teacher/...
    path('api/teacher/', include('sk.teacher_api_urls')),

    # API абитуриента /api/applicant/...
    path('api/applicant/', include('sk.applicant_api_urls')),

    # API ученика /api/student/...
    path('api/student/', include('sk.student_api_urls')),
    
    # API унифицированный дашборд для STUDENT и APPLICANT /api/dashboard/...
    path('api/dashboard/', include('sk.unified_api_urls')),

    # API платежей ЮKassa /api/payments/...
    path('api/payments/', include('sk.payment_api_urls')),
]
